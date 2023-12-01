from flask import jsonify, request
from src.sql.connect import connect_sql
from src.sql.query_f import query_item_info_by_sidlist
from src.graphdata.neo4j_f import GraphDB
import pandas as pd
import time
from src.Backend.util.filting_f import item_filting 

from src.Backend.util.para_process import *

from src.model.F.rec import list_2_2d_rec_lists


def get_search_post():
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
    rec_method = rec_method_process(args_dict)

    tags, IsTagFilter = tags_process(args_dict)
    st, et, IsTimeFilter = time_process(args_dict)
    
    topk = topk_process(args_dict)

    para_dict = {
        "type": t,
        "st": st,
        "et": et,
        "topk": topk,
        "tags": tags,
        "IsTimeFilter": IsTimeFilter,
        "IsTagFilter": IsTagFilter,
    }

    # sid_list = item_filting(para_dict)

    if rec_method == "s":
        if len(tags) > 0:
            sid_list = item_filting(para_dict, flag="search")
            if len(sid_list) == 0:
                return jsonify({'message': f"没有tag为{tags}的条目"})

            if len(sid_list) > 100:
                sid_list = sid_list[:100]

            results = query_item_info_by_sidlist(sid_list)
            user_rec_df = pd.DataFrame(results)

        else:
            return jsonify({'message': " tag 不能为空"})


    if len(user_rec_df) == 0:
        return jsonify({'message': "没有相关的记录"})
    else:
        user_rec_df.subject_type = user_rec_df.subject_type.astype(int)

        res_sid_list = list(user_rec_df.sid)
        relation_list = list_2_2d_rec_lists(res_sid_list)

        if rec_method in ["s"]:
            pass
        else:
            relation_list = relation_list[:topk]

        response_data = {
            "data": user_rec_df.to_dict("records"),
            "relation_list": relation_list
        }

        return jsonify(response_data)