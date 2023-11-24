from flask import jsonify, request
from src.sql.connect import connect_sql
from src.sql.query_f import query_uid, query_max_uid, query_item_info_by_sidlist
from src.data_spider_mysql.user_mapping_f import update_sql_by_uname
from src.datacls.ui_f import UI_cls
from src.model.seqtransfer.seqtransfer_f import SeqTransfer
from src.model.embedding.rec_f import MFRec
from src.model.SARSRec_dir.SASRec4Bangumi_dir import SASRec4Bangumi
from src.model.BanTrans_dir.BanTrans_f import Bantrans4Bangumi
from src.graphdata.neo4j_f import GraphDB
import pandas as pd
import time

from src.Backend.API.para_process import *
from src.Backend.API.filting_f import item_filting, query_tags, query_dislike_items

from src.model.F.rec import list_2_2d_rec_lists

ui_cls = UI_cls()
mfrec = MFRec(model_path="assets/MF/")

mp = "assets/sarsrec4bgm/SASRec.epoch=201.lr=0.001.layer=2.head=1.hidden=50.maxlen=200.pth"
uid_mapping_path, sid_mapping_path = "assets/sarsrec4bgm/uid_mapping.pkl", "assets/sarsrec4bgm/sid_mapping.pkl"
sarsrec = SASRec4Bangumi(mp, uid_mapping_path, sid_mapping_path)

bsrrec = Bantrans4Bangumi( 
        model_path="assets/BanTrans/gal1/process_save/model_checkpoint3.pth",
        uid_mapping_path="assets/BanTrans/gal1/process_save/uid_mapping.pkl", 
        sid_mapping_path="assets/BanTrans/gal1/process_save/sid_mapping.pkl"
    )

bsrrec_anime_nsfw = Bantrans4Bangumi( 
        model_path="assets/BanTrans/anime_nsfw_1/model10.pth",
        uid_mapping_path="assets/BanTrans/anime_nsfw_1/uid_mapping.pkl", 
        sid_mapping_path="assets/BanTrans/anime_nsfw_1/sid_mapping.pkl"
    )

bsrrec_anime = Bantrans4Bangumi( 
        model_path="assets/BanTrans/anime_1/model_a2.pth",
        uid_mapping_path="assets/BanTrans/anime_1/uid_mapping.pkl", 
        sid_mapping_path="assets/BanTrans/anime_1/sid_mapping.pkl"
    )


# @profile


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
        "topk": 2 * topk,
        "popdays": popdays,
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

    else:
        url = request.url

        if update_f:
            cached_result = None
        else:
            # cached_result = cache.get(url)
            cached_result = None

        if type(cached_result) == type(None):

            if rec_method == "pop":
                para_dict["candidate_sid"] = item_filting(para_dict)
                user_rec_df = ui_cls.rec_pop(**para_dict)
                if type(user_rec_df) == type(None):
                    return jsonify({'message': "没有相关的记录"})

                # cache.put(url, user_rec_df)

            elif rec_method in ["p", "p_dev", "MF", "sarsrec", "bsr"]:
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
                
                elif rec_method in ["bsr"]:
                    if t == 0:
                        user_rec_df = bsrrec_anime.rankitem(uid, **para_dict)
                    elif t == 2:
                        user_rec_df = bsrrec_anime_nsfw.rankitem(uid, **para_dict)
                    else:
                        user_rec_df = bsrrec.rankitem(uid, **para_dict)


                if type(user_rec_df) == type(None):
                    return jsonify({'message': "没有相关的记录"})
                # cache.put(url, user_rec_df)

        else:
            user_rec_df = cached_result

    if len(user_rec_df) == 0:
        return jsonify({'message': "没有相关的记录"})
    else:
        user_rec_df.subject_type = user_rec_df.subject_type.astype(int)

        # print(user_rec_df)
        # user_rec_df

        # if t in [1, 2, 3, 4, 6]:
        #     return jsonify(user_rec_df.query(f"subject_type == {t}").to_dict("records"))
        # else:
        res_sid_list = list(user_rec_df.sid)
        relation_list = list_2_2d_rec_lists(res_sid_list) 
        
        if rec_method in ["s"]:
            pass
        else:
            relation_list = relation_list[:topk]

        # return jsonify(user_rec_df.to_dict("records"))


        response_data = {
            "data": user_rec_df.to_dict("records"),
            "relation_list": relation_list
        }
        

        return jsonify(response_data)