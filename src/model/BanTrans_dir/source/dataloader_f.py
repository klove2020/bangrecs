
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np

def generate_sequences(df, maxlen):
    data_list, label_list = [], []
    for _, group in df.groupby('u_index'):
        s_indices = group['s_index'].values
        labels = group['label'].values
        labels[labels == 0] = -1  # 将标签为0的更改为-1
        
        for i in range(1, len(s_indices) + 1):
            data_seq = s_indices[max(0, i-maxlen):i]
            label_seq = labels[max(0, i-maxlen):i]
            
            # 对于短于maxlen的序列，我们在前面填充0
            data_seq = np.pad(data_seq, (maxlen-len(data_seq), 0), mode='constant')
            label_seq = np.pad(label_seq, (maxlen-len(label_seq), 0), mode='constant')
            
            data_list.append(data_seq)
            label_list.append(label_seq)
    
    return np.array(data_list), np.array(label_list)

