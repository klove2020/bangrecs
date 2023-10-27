from src.sql.query_f import query_uid, query_max_uid, query_item_info_by_sidlist
from src.graphdata.neo4j_f import GraphDB
import pandas as pd
import time


def uname_process(i):
    try:
        i = int(i)
    except:
        i = query_uid(i)

    return i


def subject_type_process(args_dict):
    t = args_dict.get('type', None)
    try:
        t = int(t)
        if t in [1, 2, 3, 4, 6]:
            return t
        else:
            return 0
    except:
        return 0


def update_f_process(args_dict):
    update_f = args_dict.get('update_f', False)

    if update_f in [False, True]:
        return update_f
    else:
        return False


def tags_process(args_dict):
    tags = args_dict.get('tags', '')

    # print("\n\n\n\n\n\n")
    # print(f"{type(tags) = }")
    # print(f"{(tags) = }")
    # print(f"{(tags[0]) = }")
    # print("\n\n\n\n\n\n")
    if tags == '' or tags == []:
        tags = []

    if len(tags) > 0:
        if type(tags[0]) == type([]):
            for ts in tags:
                if len(ts) == 0:
                    tags.remove(ts)

    IsTagFilter = args_dict["IsTagFilter"]
    if len(tags) == 0:
        IsTagFilter = False

    return tags, IsTagFilter


def time_process(args_dict):
    s_date = args_dict.get('startDate', pd.Timestamp(1900, 1, 1))
    e_date = args_dict.get('endDate', pd.Timestamp(time.time(), unit="s"))

    IsTimeFilter = args_dict["IsTimeFilter"]

    try:
        st = pd.Timestamp(s_date)
    except:
        st = pd.Timestamp(1900, 1, 1)

    try:
        et = pd.Timestamp(e_date)
    except:
        et = pd.Timestamp(time.time(), unit="s")

    return st, et, IsTimeFilter


def topk_process(args_dict):
    try:
        topk = args_dict.get('topk', 20)
        topk = int(topk)
        assert 1 <= topk <= 100
    except:
        topk = 20

    return topk


def popdays_process(args_dict):
    try:
        popdays = args_dict.get("popdays", 7)
        popdays = int(popdays)
        assert 1 <= popdays <= 365
    except:
        popdays = 7
    return popdays


def rec_method_process(args_dict):
    rec_method = args_dict.get('strategy', "p")
    # if rec_method not in ["pop", "p", "s"]:
    #     rec_method = "pop"
    return rec_method
