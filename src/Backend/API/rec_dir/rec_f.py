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

from src.model.F.rec import list_2_2d_rec_lists

from src.Backend.API.cache_dir.cache_f import cache

ui_cls = UI_cls()

from .load_model_f import mfrec, sarsrec,  ht 

def get_rec_post(uname, table_name):
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
    }


    if rec_method == "pop":

        cache_key = f"{t}+{topk}+{st}+{et}+{IsTagFilter}+{IsTimeFilter}+{tags}"
        cache_res = cache.get(cache_key)

        if type(cache_res) == type(None):

            para_dict["candidate_sid"] = item_filting(para_dict)
            user_rec_df = ui_cls.rec_pop(**para_dict)
            if type(user_rec_df) == type(None):
                return jsonify({'message': "没有相关的记录"})
            else:
                cache.set(cache_key, user_rec_df, timeout=86400)
        
        else:
            print("get cache")
            user_rec_df = cache_res

    elif rec_method in ["p", "p_dev", "MF", "sarsrec", "HT"]:
        uid = uname_process(uname)

        max_uid = query_max_uid()
        if type(uid) == int:
            if 0 < uid <= max_uid:
                pass
            else:
                return jsonify({'message': f"{uid} 超过出用户id范围"})
        else:
            uid = update_sql_by_uname(uname)
            if type(uid) == type(None):
                return jsonify({'message': f"没有用户名为{uname}的用户"})

        dislike_item_list = query_dislike_items(uid)
        l0 = item_filting(para_dict)
        l0 = list(set(l0) - set(dislike_item_list))

        para_dict["candidate_sid"] = l0

        ui_cls.update_collect_table_one_user(uid, update_f=update_f)
        user = ui_cls.get_user(uid)
        user.receive_query()

        if rec_method in ["p", "p_dev"]:
            m = SeqTransfer(table_name)
            user_rec_df = m.rec(uid, **para_dict)

        elif rec_method in ["MF"]:
            user_rec_df = mfrec.rec(uid, **para_dict)

        elif rec_method in ["sarsrec"]:
            user_rec_df = sarsrec.rankitem(uid, **para_dict)

        elif rec_method in ["HT"]:
            user_rec_df = ht.rankitem(uid, **para_dict)

        if type(user_rec_df) == type(None):
            return jsonify({'message': "没有相关的记录"})

        if len(user_rec_df) == 0:
            return jsonify({'message': "没有相关的记录"})

        # cache.put(url, user_rec_df)


    if len(user_rec_df) == 0:
        return jsonify({'message': "没有相关的记录"})
    else:
        user_rec_df.subject_type = user_rec_df.subject_type.astype(int)

        res_sid_list = list(user_rec_df.sid)
        relation_list = list_2_2d_rec_lists(res_sid_list)

        if rec_method in ["s"]:
            pass
        elif rec_method in ["pop"]:
            pass
        else:
            relation_list = relation_list[:topk]

        response_data = {
            "data": user_rec_df.to_dict("records"),
            "relation_list": relation_list
        }

        return jsonify(response_data)
