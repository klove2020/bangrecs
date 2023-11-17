import pickle
from src.model.F.rec import get_read_item_id, check_sid_list, get_read_item_id4SARS
from src.sql.query_f import query_item_info_by_sidlist
from src.sql.connect import connect_sql

import torch
import numpy as np
import pandas as pd

from .source.model_f import Bantrans

class Bantrans4Bangumi(Bantrans):
    def __init__(self, model_path, uid_mapping_path, sid_mapping_path):

        with open(uid_mapping_path, 'rb') as f:
            self.uid_to_uindex, self.uindex_to_uid = pickle.load(f)

        with open(sid_mapping_path, 'rb') as f:
            self.sid_to_sindex, self.sindex_to_sid = pickle.load(f)

        user_num = max(self.uindex_to_uid.keys())
        item_num = max(self.sindex_to_sid.keys())

        super().__init__(item_num + 1, d = 32, maxlen = 200, device = "cpu")

        self.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.eval()

        self.sid_candidate_set = set(self.sid_to_sindex.keys())

    def predict(self, readed_tuple, candidate_s_indics):
        s_indics, labels = readed_tuple 

        data_seq = np.array(s_indics[-self.maxlen:]) # (len,)
        label_seq = np.array(labels[-self.maxlen:]) # (len,)
        
        # # 对于短于maxlen的序列，我们在前面填充0


      # 扩展data_seq和label_seq使其与candidate_s_indics的长度匹配
        repeated_data_seq = np.tile(data_seq, (len(candidate_s_indics), 1)) # (len(candidiate_s_indics), n)
        repeated_label_seq = np.tile(label_seq, (len(candidate_s_indics), 1)) # (len(candidiate_s_indics), n)

        # 构建list_ma
        list_ma = np.column_stack((repeated_data_seq, candidate_s_indics))

        # 构建两种标签label_ma_p1和label_ma_n1
        label_ma_p1 = np.column_stack((repeated_label_seq, np.ones(len(candidate_s_indics))))
        label_ma_n1 = np.column_stack((repeated_label_seq, -1 * np.ones(len(candidate_s_indics))))
        

        list_ma = torch.tensor(list_ma, dtype=int).to(self.device)
        label_ma_p1 = torch.tensor(label_ma_p1, dtype=int).to(self.device)
        label_ma_n1 = torch.tensor(label_ma_n1, dtype=int).to(self.device)

        pos_score = self.forward(list_ma, label_ma_p1)
        neg_score = self.forward(list_ma, label_ma_n1)
        return pos_score - neg_score

    def rankitem_sids(self, collect_df, candidate_sid_list):

        if len(collect_df) != 0:

            collect_df = collect_df[collect_df.sid.isin(self.sid_candidate_set)]
            
            sids = list(collect_df.sid)
            s_indics = [self.sid_to_sindex[i] for i in sids][-self.maxlen:]
            readed_label = collect_df.rate.apply(lambda x: 1 if x>6 else 0)

            


        else:
            s_indics = []
            readed_label = []

        candidate_sids = [sid for sid in candidate_sid_list if sid in self.sid_candidate_set]
        candidate_s_indics = [self.sid_to_sindex[i] for i in candidate_sids]
        
        
        ########
        score = self.predict((s_indics, readed_label), candidate_s_indics) # (1, N)
        score = score.tolist()
        ########

        df = pd.DataFrame(np.array([candidate_sids, score]).T, columns=["sids", "score"])
        df = df.sort_values(by="score", ascending=False)
        df.sids = df.sids.astype(int)
        df = df.set_index("sids")
        return df
        # return list(df.sids)

    def rankitem(self, uid, **args):

        read_item_id = get_read_item_id(uid, return_type="list")
        
        topk = args.get("topk", 10)
        candidate_sid_list = args["candidate_sid"]
        candidate_sid_list = list( set(candidate_sid_list) - set(read_item_id))
        if len(candidate_sid_list) == 0:
            return None
        
        # _read_item_id = filtering(read_item_id)
        conn, cursor = connect_sql(dict=1)
        query = f"SELECT sid,rate from collect WHERE uid = {uid} AND `type` = 2 AND rate > 0"
        cursor.execute(query)
        res = cursor.fetchall()
        collect_df = pd.DataFrame(res)


        ranked_df = self.rankitem_sids(collect_df, candidate_sid_list)

        res_sid_list  = check_sid_list(list(ranked_df.index), set(read_item_id), uid, topk)
        res_df = pd.DataFrame(query_item_info_by_sidlist(sid_list = res_sid_list))

        if len(res_df) == 0:
            return None

        
        topk_score = ranked_df.loc[list(res_df.sid)].score
        
        res_df["trans_score"] = list(topk_score)
        # res_df = res_df[res_df["trans_score"] > 0]

        return res_df.sort_values(by="trans_score", ascending=False)


