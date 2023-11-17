import torch


import torch.nn as nn

import torch.nn.functional as F

class Bantrans(nn.Module):
    def __init__(self, N, d = 32, maxlen = 200, device = "cpu", lr=0.01, dropout_rate=0.2) -> None:
        """
            N:候选物品总数量
            maxlen:序列最大长度
        """
        super().__init__()
        self.N = N
        self.d = d
        self.maxlen = 200
        self.device = device
        self.lr = lr
        
        self.I_s = nn.Parameter(torch.randn(N+1, d))
        self.I_p = nn.Parameter(torch.randn(N+1, d))
        self.I_n = nn.Parameter(torch.randn(N+1, d))

        self.to(device=self.device)
        self.adam_optimizer = torch.optim.Adam(self.parameters(), lr=self.lr, betas=(0.9, 0.98))

        # self.dropout = nn.Dropout(dropout_rate)  # 添加dropout层
        self.p = dropout_rate



    def forward(self, list_ma, label_ma):
        """
            list_ma : n * maxlen 两维度item索引矩阵
            label_ma: n * maxlen 两维度item标签矩阵, 有+1,-1,0
        """
        SoftM = self.I_s[list_ma] # n * maxlen * d

        PosM = self.I_p[list_ma] # n * maxlen * d
        NegM = self.I_n[list_ma] # n * maxlen * d

        # 创建掩码
        pos_mask = (label_ma == 1).unsqueeze(-1).expand_as(PosM)
        neg_mask = (label_ma == -1).unsqueeze(-1).expand_as(NegM)

        # 应用掩码
        PosM_masked = PosM * pos_mask
        NegM_masked = NegM * neg_mask
        embedding = PosM_masked + NegM_masked

        # 对embedding的最后一个维度进行dropout
        dropout_mask = torch.ones(embedding.size(0), embedding.size(1), 1).to(embedding.device)
        dropout_mask[:, :-1, :] = F.dropout(dropout_mask[:, :-1, :], p=self.p, training=self.training)
        embedding *= dropout_mask

        # 获取SoftM最后一列的向量
        last_col = SoftM[:, -1, :]  # n * d
        rest_cols = SoftM[:, :-1, :]  # n * (maxlen-1) * d
        
        # 为了实现逐个元素的内积，我们使用了bmm函数 (batch matrix multiplication)
        scores_weight = torch.bmm(rest_cols, last_col.unsqueeze(2))  # n * (maxlen-1) * 1

        # 移除最后一个维度并逐行应用softmax
        scores_weight = F.softmax(scores_weight, dim=1)  # n * (maxlen-1)

        # 将scores_weight分配到embedding的前maxlen-1列并进行累和
        weighted_embedding = embedding[:, :-1, :] * scores_weight  # n * (maxlen-1) * d
        weighted_sum = weighted_embedding.sum(dim=1)  # n * d

        # 获取embedding的最后一列
        last_col_embedding = embedding[:, -1, :]  # n * d

        # 计算最终分数（内积）
        final_scores = (weighted_sum * last_col_embedding).sum(dim=1)  # n

        
        return final_scores  # 返回最终的分数
    
    def train_iter(self, list_ma, label_ma):
        """
            list_ma : n * maxlen 两维度item索引矩阵
            label_ma: n * maxlen 两维度item标签矩阵, 有+1,-1,0
        """
        # 反转最后一列的标签
        inverse_label_ma = label_ma.clone()  # 创建一个label_ma的副本
        inverse_label_ma[:,-1] *= -1  # 反转最后一列的标签

        score = self.forward(list_ma, label_ma)
        inverse_score = self.forward(list_ma, inverse_label_ma)

        eps = 1e-6
        loss = - torch.log(torch.sigmoid(score - inverse_score) + eps).mean()
        self.adam_optimizer.zero_grad()
        loss.backward()
        self.adam_optimizer.step()

        return loss.item()
    

    def train_model(self, train_loader, epochs):
        """
        训练模型的函数。
        
        参数:
            model: Bantrans模型的实例。
            train_loader: 包含训练数据的DataLoader。
            epochs: 要训练的epoch数。
        """
        self.train()  # 设置模型为训练模式
        for epoch in range(epochs):
            total_loss = 0
            num = 0
            all_iter_num = len(train_loader)
            for list_ma, label_ma in train_loader:
                num += 1
                
                # 将数据和标签移至正确的设备
                list_ma, label_ma = list_ma.to(self.device), label_ma.to(self.device)

                # 执行单次训练迭代并累加损失
                loss = self.train_iter(list_ma, label_ma)

                if num % 100 == 0:
                    print(f"Epoch {epoch+1}/{epochs}, Iter: {num}/ {all_iter_num}, Loss: {loss:.4f}")

                total_loss += loss

            avg_loss = total_loss / len(train_loader)
            print(f"Epoch {epoch+1}/{epochs}, Average Loss: {avg_loss:.4f}")

            if (epoch+1) % 10 == 0:
                save_model(self)


def save_model(model, path="model_checkpoint.pth"):
    """保存模型参数到指定路径"""
    torch.save(model.state_dict(), path)

def load_model(model, path="model_checkpoint.pth"):
    """从指定路径加载模型参数"""
    model.load_state_dict(torch.load(path))
    model.to(model.device)  # 确保加载模型到正确的设备
