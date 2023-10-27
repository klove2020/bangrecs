from src.sql.connect import connect_sql
import pandas as pd
import numpy as np
import time
from src.model.seqtransfer.F import select_history_seq
from src.sql.query_f import query_item_info_by_sidlist, query_max_sid

from src.model.F.rec import get_read_item_id, check_sid_list

class SeqTransfer:
    def __init__(self, table_name = "trans_ma") -> None:
        """
            只做正交互聚合
        """
        self.table_name = table_name

    # @profile
    def rec(self, uid, **args):
        
        topk = args.get("topk", 10)
        sid_list = args["candidate_sid"]

        max_sid = query_max_sid()
        score_arr = np.zeros(max_sid + 1)

        df = select_history_seq(uid, **args)
            
        # print(f"{df = }")

        if len(df) == 0:
            args["IsTagFilter"] = 0
            df = select_history_seq(uid, **args)
            if len(df) == 0:
                return None
        

        zero_ts = df.iloc[-1].timestamp - 3600 * 24 * 7
        one_ts = time.time()

        def weight_t(ts):
            min_w = 0.2
            y = (1 - min_w)/(one_ts - zero_ts) * (ts - zero_ts) + min_w
            return y

        conn, cursor = connect_sql(dict=1)
        for i, row in df.iterrows():
            rate = row.rate
            type_ = row["type"]
            ts = row.timestamp
            sid = row.sid

            time_weight = weight_t(ts)
            if type_ == 1:
                s = 0.5
            elif type_ == 3:
                if rate >= 7:
                    s = 0.7
                else:
                    s = 0.5
            elif type_ == 2:
                if rate >= 9:
                    s = 1.5
                elif rate >= 7:
                    s = 1
                else:
                    s = 0.5
            
            score_weight = s * time_weight
            query = f"SELECT * FROM {self.table_name} WHERE `sid` = {sid} AND trans_score >= 0;"
            cursor.execute(query)
            res = cursor.fetchall()
            score_df = pd.DataFrame(res)

            if len(score_df) == 0:
                continue
            sid_index = score_df.trans_sid.to_numpy() 
            sid_score = score_df.trans_score.to_numpy() 

            score_arr[sid_index] += score_weight * sid_score
        
        query = f"SELECT sid from collect WHERE uid = {uid}"
        cursor.execute(query)
        res = cursor.fetchall()
        read_item_id = pd.DataFrame(res).sid.to_numpy() 
        read_item_id[read_item_id > max_sid] = 0


        score_arr[read_item_id] = 0

        new_score_arr = np.zeros_like(score_arr)            
        new_score_arr[sid_list] = score_arr[sid_list]
        score_arr = new_score_arr

        _res_sid_list = (-score_arr).argsort()
        res_sid_list = []

        
        care_rel_type_list = [1, 1002, 1003, 1007, 1008, 4, 5, 6, 12, 4006, 4012]
        previous_subject_rel_type_list = [1005, 2, 4002]
        follow_subject_rel_type_list = [1006, 3, 4003]
        care_rel_type_list =  care_rel_type_list  + previous_subject_rel_type_list + follow_subject_rel_type_list


        query = f"SELECT sid from collect WHERE uid = {uid} AND `type` = 2"
        cursor.execute(query)
        readed_item_id = pd.DataFrame(cursor.fetchall()).sid.to_numpy() 
        readed_item_id[readed_item_id > max_sid] = 0
        
        read_item_id_set = set(readed_item_id)

        for check_sid in _res_sid_list:
            s = score_arr[check_sid]
            if s <= 0:
                break

            query = f"SELECT * FROM `SubjectRelations` WHERE `subject_id` = {check_sid};"
            cursor.execute(query)
            
            relation_df = pd.DataFrame(cursor.fetchall())
            if len(relation_df) == 0:
                res_sid_list.append(check_sid)
            else:
                relation_df = relation_df[relation_df.relation_type.isin(care_rel_type_list)]

                
                previous_subjects_set = set(relation_df.related_subject_id[relation_df.relation_type.isin(previous_subject_rel_type_list)])

                ## 有相关的前传作品
                if len(previous_subjects_set) > 0:
                    ss_ = previous_subjects_set & read_item_id_set
                    
                    ## 一部没读过
                    if len(ss_) == 0:
                        continue
                    ## 有读过的
                    else:
                        pass
                else:
                    pass

                rsid_set = set(relation_df.related_subject_id)
                read_rel_sid_list =  list(read_item_id_set & rsid_set)

                ## 相关作品一部没看过
                if len(read_rel_sid_list) == 0:
                    res_sid_list.append(check_sid)
                
                else:
                    conn, cursor = connect_sql(dict=1)
                    
                    
                    if len(read_rel_sid_list) == 1:
                        qs = f"={read_rel_sid_list[0]}"
                    else:
                        qs = f"IN {tuple(read_rel_sid_list)}"
                    query = f"""
                            SELECT * 
                            FROM collect 
                            WHERE uid = {uid}
                            AND sid {qs}
                            AND ((type IN (4, 5)) OR (rate <= 4 AND rate >= 1));
                            """
                    cursor.execute(query)
                    
                    c_df_ = pd.DataFrame(cursor.fetchall())
                    ## 没有负面评价的作品
                    if len(c_df_) == 0:
                        res_sid_list.append(check_sid)
                    ## 有就跳过
                    else:
                        continue
            
            if len(res_sid_list) >= topk:
                break


        if len(res_sid_list) == 0:
            return None

        res_df = pd.DataFrame(query_item_info_by_sidlist(sid_list = res_sid_list))

        if len(res_df) == 0:
            return None

        res_score_list = score_arr[list(res_df.sid)]
        res_df["trans_score"] = list(res_score_list)

        return res_df.sort_values(by="trans_score", ascending=False)

