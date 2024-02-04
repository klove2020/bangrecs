from flask import jsonify, request
from src.sql.connect import connect_sql
from src.sql.query_f import query_uid, query_max_uid, query_item_info_by_sidlist
from src.data_spider_mysql.user_mapping_f import update_sql_by_uname
from src.datacls.ui_f import UI_cls
from src.model.seqtransfer.seqtransfer_f import SeqTransfer
from src.graphdata.neo4j_f import GraphDB
import pandas as pd
import time

from src.Backend.util.para_process import *
from src.Backend.util.filting_f import item_filting, query_tags, query_dislike_items

ui_cls = UI_cls()

# @profile
def get_rec_app2(uname, table_name):
    """
    args_dict:
        type
        update_f
        strategy

        IsTimeFilter
        IsTagFilter

        startDate
        endDate

        topk
        popdays
        tags
    """
    args_dict = request.json

    print(args_dict)

    t = subject_type_process(args_dict)
    update_f = update_f_process(args_dict)
    rec_method = rec_method_process(args_dict)

    tags, IsTagFilter = tags_process(args_dict)
    st, et, IsTimeFilter = time_process(args_dict)

    popdays = popdays_process(args_dict)
    topk = topk_process(args_dict)

    

    para_dict = {
        "type": t,
        "st": st,
        "et": et,
        "topk": topk,
        "popdays": popdays,
        "tags": tags,
        "IsTimeFilter": IsTimeFilter,
        "IsTagFilter": IsTagFilter,
        "collects":args_dict["collects"]
    }

    
    uid = uname_process(uname)

    max_uid = 10000000
    if type(uid) == int:
        if 0 < uid <= max_uid:
            pass
        else:
            return jsonify({'message': f"{uid} 超过出用户id范围"})
    else:
        uid = update_sql_by_uname(uname)
        if type(uid) == type(None):
            return jsonify({'message': f"没有用户名为{uname}的用户"})

    # dislike_item_list = query_dislike_items(uid)
    
    l0 = item_filting(para_dict)
    # l0 = list(set(l0) - set(dislike_item_list))

    para_dict["candidate_sid"] = l0

    # ui_cls.update_collect_table_one_user(uid, update_f=update_f)
    # user = ui_cls.get_user(uid)
    # user.receive_query()

    m = SeqTransfer(table_name)
    user_rec_df = m.rec(uid, **para_dict)


    if type(user_rec_df) == type(None):
        return jsonify({'message': "没有相关的记录"})
    
    if len(user_rec_df) == 0:
        return jsonify({'message': "没有相关的记录"})
    else:
        user_rec_df.subject_type = user_rec_df.subject_type.astype(int)

        user_rec_df["score"] = user_rec_df["trans_score"] 
        user_rec_df = user_rec_df[["sid", "score"]]
        
        response_data = {
            "data": user_rec_df.to_dict("records"),
        }

        return jsonify(response_data)
