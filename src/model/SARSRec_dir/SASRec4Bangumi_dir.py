import pickle
from src.model.F.rec import get_read_item_id, check_sid_list, get_read_item_id4SARS
from src.sql.query_f import query_item_info_by_sidlist

class arg_init:
    def __init__(self):
        self.device = "cpu"
        self.hidden_units = 50
        self.maxlen = 200
        self.dropout_rate = 0.2
        self.num_blocks = 2
        self.num_heads = 1


import torch
import numpy as np
import pandas as pd

from .source import SASRec

class SASRec4Bangumi(SASRec):
    def __init__(self, model_path, uid_mapping_path, sid_mapping_path):
        args = arg_init()

        with open(uid_mapping_path, 'rb') as f:
            self.uid_to_uindex, self.uindex_to_uid = pickle.load(f)

        with open(sid_mapping_path, 'rb') as f:
            self.sid_to_sindex, self.sindex_to_sid = pickle.load(f)

        user_num = max(self.uindex_to_uid.keys())
        item_num = max(self.sindex_to_sid.keys())

        super().__init__(user_num, item_num, args)

        self.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.eval()

        self.sid_candidate_set = set(self.sid_to_sindex.keys())

    def rankitem_sids(self, sids, candidate_sid_list):
        sids = [sid for sid in sids if sid in self.sid_candidate_set]
        s_indics = [self.sid_to_sindex[i] for i in sids][-self.maxlen:]
        

        candidate_sids = [sid for sid in candidate_sid_list if sid in self.sid_candidate_set]
        candidate_s_indics = [self.sid_to_sindex[i] for i in candidate_sids]
        
        # candidate_s_indics =  list(set(range(1, self.item_num+1)) - set(s_indics))
        # candidate_sids = [self.sindex_to_sid[i] for i in candidate_s_indics]
        
        
        score = self.predict(None, np.array([s_indics]), candidate_s_indics) # (1, N)
        score = score[0].tolist()

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
        
        _read_item_id = get_read_item_id4SARS(uid)
        ranked_df = self.rankitem_sids(_read_item_id, candidate_sid_list)

        res_sid_list  = check_sid_list(list(ranked_df.index), set(read_item_id), uid, topk)
        res_df = pd.DataFrame(query_item_info_by_sidlist(sid_list = res_sid_list))

        if len(res_df) == 0:
            return None

        
        topk_score = ranked_df.loc[res_sid_list].score
        
        res_df["trans_score"] = list(topk_score)
        # res_df = res_df[res_df["trans_score"] > 0]

        return res_df.sort_values(by="trans_score", ascending=False)


