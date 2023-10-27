import numpy as np
import torch
from torch import nn
from torch.optim import SGD

from src.sql.connect import connect_sql
import pandas as pd
from src.model.embedding.vecsql_f import store_Utensor2sql, store_Itensor2sql

class MF(nn.Module):
    def __init__(self, uid_list, sid_list, d, lr) -> None:
        super().__init__()
        M = len(uid_list)
        N = len(sid_list)
        self.M = M
        self.N = N
        self.d = d

        self.uid_list = uid_list
        self.sid_list = sid_list
    
        self.U = nn.Parameter( torch.zeros(M, d))
        self.I = nn.Parameter( torch.randn(N, d))
        

        self.construct_id_index_map(uid_list, sid_list)
        self.optimizor = SGD(self.parameters(), lr = lr)

    def construct_id_index_map(self, uid_list, sid_list):
        self.uid_2_uindex = {uid: index for index, uid in enumerate(uid_list)}
        self.sid_2_sindex = {sid: index for index, sid in enumerate(sid_list)}

        self.uindex_2_uid = {index: uid for uid, index in self.uid_2_uindex.items()}
        self.sindex_2_sid = {index: sid for sid, index in self.sid_2_sindex.items()}


    def train_one_iter(self, df):
        s_index = list(df.sid.apply(lambda x: self.sid_2_sindex[x]))
        u_index = list(df.uid.apply(lambda x: self.uid_2_uindex[x]))
        rate = torch.tensor(list(df.rate))

        loss = (((self.U[u_index] * self.I[s_index]).sum(1) - rate) ** 2).mean()
        self.optimizor.zero_grad()
        loss.backward()
        self.optimizor.step()

        return loss.item()
    
    def train(self, n_epochs):
        for epoch in range(n_epochs):
            count = 0
            bs = sample()
            for batch_ids in bs:
                count += 1
                # 对于每一个mini-batch，我们从数据库中获取相应的DataFrame
                conn, cursor = connect_sql(dict=1)
                ids_str = ",".join(map(str, batch_ids))
                query = f"SELECT sid, uid, rate FROM collectForTrain WHERE id IN ({ids_str})"
                cursor.execute(query)
                batch_data = cursor.fetchall()
                df = pd.DataFrame(batch_data)
                loss = self.train_one_iter(df)
                if count % 100 == 0:
                    print(f"{epoch=}, iter= {count} / {len(bs)}, {loss=}")

    def save_model(self):
        U = self.U.detach().numpy()
        np.save("MF_U.npy",U)

        I = self.I.detach().numpy()
        np.save("MF_I.npy",I)

        np.save("MF_uid_list.npy", np.array(self.uid_list))
        np.save("MF_sid_list.npy", np.array(self.sid_list))

        # store_Utensor2sql(self.uid_list, self.U)
        # store_Itensor2sql(self.sid_list, self.I)
        

def sample(batch_size=64, shuffle=True):
    conn, cursor = connect_sql(dict=1)
    query = "SELECT MAX(id) FROM collectForTrain"
    cursor.execute(query)
    res = cursor.fetchall()
    df = pd.DataFrame(res)
    id_max = df.iloc[0,0]
    ids = list(range(id_max))

    if shuffle:
        np.random.shuffle(ids)
    
    # 将ID列表划分为mini-batches
    n_batches = len(ids) // batch_size
    batches = [ids[i*batch_size:(i+1)*batch_size] for i in range(n_batches)]
    
    # 如果ID的数量不是batch_size的整数倍，则还会有一个大小不是batch_size的最后一个batch
    if len(ids) % batch_size != 0:
        batches.append(ids[n_batches*batch_size:])
    
    return batches
