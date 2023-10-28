import numpy as np
from src.sql.query_f import query_item_info_by_sidlist, query_max_sid

from src.sql.connect import connect_sql
import pandas as pd


def get_read_item_id(uid, return_type = "set"):
    conn, cursor = connect_sql(dict=1)
    query = f"SELECT sid from collect WHERE uid = {uid}"
    cursor.execute(query)
    res = cursor.fetchall()
    if return_type == "set":
        read_item_id = set(list(pd.DataFrame(res).sid))
    elif return_type == "list":
        read_item_id = list(pd.DataFrame(res).sid)
    else:
        assert False
        
    return read_item_id


def get_read_item_id4SARS(uid):
    conn, cursor = connect_sql(dict=1)
    query = f"SELECT sid from collect WHERE uid = {uid} AND type = 2 AND rate > 5"
    cursor.execute(query)
    res = cursor.fetchall()

    read_item_id = list(pd.DataFrame(res).sid)
        
    return read_item_id


def check_sid_list(_res_sid_list, read_item_id_set, uid, topk):
    res_sid_list = []
    care_rel_type_list = [1, 1002, 1003, 1007, 1008, 4, 5, 6, 12, 4006, 4012]
    previous_subject_rel_type_list = [1005, 2, 4002]
    follow_subject_rel_type_list = [1006, 3, 4003]
    care_rel_type_list =  care_rel_type_list  + previous_subject_rel_type_list + follow_subject_rel_type_list

    conn, cursor = connect_sql(dict=1)

    for check_sid in _res_sid_list:

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

    return res_sid_list  
