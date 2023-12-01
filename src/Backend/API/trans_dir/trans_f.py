from flask import jsonify, request
from src.sql.connect import connect_sql
from src.sql.query_f import query_uid,query_max_uid, query_item_info_by_sidlist
from src.datacls.ui_f import UI_cls

import pandas as pd
import numpy as np

# from src.sql.F import quick_filting_predata
from src.Backend.util.para_process import *

from src.model.F.rec import list_2_2d_rec_lists

ui_cls = UI_cls()

# @profile
def get_trans_post(sid = None, trans_ma_name = "trans_ma"):
    """
    args_dict:
    """
    # trans_ma_name = "trans_ma"
    args_dict = request.json
    
    t = subject_type_process(args_dict)
    update_f = update_f_process(args_dict)
    rec_method = rec_method_process(args_dict)

    tags, IsTagFilter = tags_process(args_dict)
    st,et,IsTimeFilter = time_process(args_dict)

    popdays = popdays_process(args_dict)
    topk = topk_process(args_dict)


    para_dict = {
        "type":t,
        "st":st,
        "et":et,
        "topk":topk,
        "popdays":popdays,
        "tags":tags,
        "IsTimeFilter":IsTimeFilter,
        "IsTagFilter":IsTagFilter,
    }

    try:
        sid = int(sid)
    except:
        return jsonify({ 'message': "条目id要为合理整数"})

    conn, cursor = connect_sql(dict=1)
    query = f"""
            SELECT * FROM {trans_ma_name} WHERE `sid` = {sid} ORDER BY `trans_score` desc LIMIT {topk} 
            """
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())

    if len(df) == 0:
        return jsonify({ 'message': f"条目{sid}不在推荐列表中"})

    sid_list = list(df.trans_sid)
    sid_list = [sid] + sid_list
    
    trans_score_list = list(df.trans_score)
    trans_score_list = [1000] + trans_score_list

    dd = {sid:s for sid,s in zip(sid_list, trans_score_list)}
    user_rec_df = pd.DataFrame(query_item_info_by_sidlist(sid_list))
    
    user_rec_df["trans_score"] = user_rec_df.sid.apply(lambda s:dd[s])
    user_rec_df = user_rec_df.sort_values(by="trans_score", ascending=False)
    # user_rec_df.iloc[0].trans_score = 0
    
    if len(user_rec_df) == 0:
        return jsonify({ 'message': "没有相关的记录"})
    else:
        user_rec_df.subject_type = user_rec_df.subject_type.astype(int)
        if t in [1,2,3,4,6]:            
            user_rec_df = user_rec_df.query(f"subject_type == {t}")            
        else:
            pass

        res_sid_list = list(user_rec_df.sid)
        relation_list = [[i] for i in res_sid_list][:topk] 
        
        response_data = {
            "data": user_rec_df.to_dict("records"),
            "relation_list": relation_list
        }

        return jsonify(response_data)