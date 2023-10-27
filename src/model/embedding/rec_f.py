import numpy as np
from src.sql.query_f import query_item_info_by_sidlist, query_max_sid

from src.sql.connect import connect_sql
import pandas as pd
from src.model.F.rec import get_read_item_id, check_sid_list

class MFRec:
    def __init__(self, model_path = "./") -> None:
        self.uid_list = np.load(model_path + "MF_uid_list.npy")
        self.sid_list = np.load(model_path + "MF_sid_list.npy")
        self.U = np.load(model_path + "MF_U.npy")
        self.I = np.load(model_path + "MF_I.npy")

        self.M = len(self.uid_list)
        self.N = len(self.sid_list)

        # 该类只构建一次，长期存在内存中
        self.uid_2_uindex = {uid: index for index, uid in enumerate(self.uid_list)}
        self.sid_2_sindex = {sid: index for index, sid in enumerate(self.sid_list)}
        self.uindex_2_uid = {index: uid for uid, index in self.uid_2_uindex.items()}
        self.sindex_2_sid = {index: sid for sid, index in self.sid_2_sindex.items()}



    def rec(self, uid, **args):

        read_item_id = get_read_item_id(uid)
        topk = args.get("topk", 10)
        sid_list = args["candidate_sid"]

        sid_list = list( set(sid_list) & set(self.sid_list) - read_item_id)
        if len(sid_list) == 0:
            return None
        sid_index = [self.sid_2_sindex[i] for i in sid_list]


        try:
            uindex = self.uid_2_uindex[uid]
        except:
            return None
        
        u_vec = self.U[uindex]
        
        print(f"{self.U.shape=}")
        print(f"{self.I.shape=}")
        print(f"{uindex=}")

        score  = self.I @ u_vec
        valid_indices = np.zeros(score.shape, dtype=bool)
        valid_indices[sid_index] = True
        # 使用布尔索引将无效索引的得分设置为负无穷
        score[~valid_indices] = -100
        

        # topk_score_s_index = (-score).argsort()[:topk]
        # res_sid_list = [self.sindex_2_sid[i] for i in topk_score_s_index]

        score_s_index = (-score).argsort()
        _res_sid_list = [self.sindex_2_sid[i] for i in score_s_index]
        res_sid_list = check_sid_list(_res_sid_list, read_item_id, uid, topk)




        res_df = pd.DataFrame(query_item_info_by_sidlist(sid_list = res_sid_list))

        if len(res_df) == 0:
            return None

        topk_score_s_index = [self.sid_2_sindex[i] for i in list(res_df.sid)]
        topk_score = score[topk_score_s_index]

        
        res_df["trans_score"] = list(topk_score)
        res_df = res_df[res_df["trans_score"] > 0]

        return res_df.sort_values(by="trans_score", ascending=False)


