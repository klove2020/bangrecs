import pandas as pd
from src.sql.connect import connect_sql
import numpy as np
from src.graphdata.neo4j_f import GraphDB


observe_time = 3600*24*14

def time_w(item_collect_time, seq_item_collect_time):
    delta = seq_item_collect_time - item_collect_time

    assert delta >= 0
    
    if delta <= 3600:
        return 0
    elif 3600 <= delta <= observe_time :
        return linear_weight_f(delta)
    else:
        return 0

def linear_weight_f(t):
    return (0 - 1)/(observe_time - 3600) * (t - observe_time)

def tag_similar_weight(tag_list1, tag_list2):
    if len(tag_list1) == 0 or len(tag_list2) == 0:
        return 0
    else:
        s1 = set(tag_list1)
        s2 = set(tag_list2)  
        
        s1_num = len(s1)
        s2_num = len(s2)
        
        if s1_num < 10 and s2_num < 10:
            if s1_num <= s2_num:
                s1_num = 10
            else:
                s2_num = 10

        return len(s1&s2) / ( np.sqrt(s1_num) * np.sqrt(s2_num) )

def select_history_seq(uid, **args):
    num = 10

    type_ = args["type"]
    IsTagFilter = args["IsTagFilter"]

    collects = args.get("collects", None)

    InCollects = False
    if type(collects) != type(None):
        InCollects = True
        ddf = pd.DataFrame(collects).query("type == 2 and (rate >= 0 or rate >= 5)")
        ddf["timestamp"] = ddf["updated_at"].apply(lambda x:pd.Timestamp(x).timestamp())
        ddf = ddf.sort_values(by="timestamp",ascending=False)
        ddf["sid"] = ddf["subject_id"]
        

    if IsTagFilter:
        tags = args["tags"]
        gb = GraphDB()
        sid_list = gb.find_subjects_by_tags(tags)
        # print(f"{sid_list=}")
        if len(sid_list) == 0:
            return []
        
        elif len(sid_list) == 1:
            excmd = f" AND sid = {sid_list[0]} "
        
        else:
            excmd = f" AND sid in {tuple(sid_list)} "

        if InCollects:
            ddf = ddf[ddf["subject_id"].isin([sid_list])]
    else:
        excmd = " AND TRUE "

    if type_ == 1:
        if InCollects:
            search_types = [1,2]
            ddf_ = ddf[ddf["subject_type"].isin(search_types)]
            df = ddf_.iloc[:num]
        else:
            typecmd = f" AND subject_type in (1,2) "
            df = _query2df(uid, typecmd + excmd)
    
    elif type_ in [2, 6]:
        if InCollects:
            search_types = [type_]
            ddf_ = ddf[ddf["subject_type"].isin(search_types)]
            df = ddf_.iloc[:num]
        else:
            typecmd = f" AND subject_type = {type_} "
            df = _query2df(uid, typecmd + excmd)
    
    elif type_ == 4:
        if InCollects:
            ddf_ = ddf[ddf["subject_type"].isin([4])]
            df1 = ddf_.iloc[:int(num*0.8)]
            ddf_ = ddf[ddf["subject_type"].isin([2])]
            df2 = ddf_.iloc[:int(num*0.2)]
        else:
            typecmd = f" AND subject_type = {4} "
            df1 = _query2df(uid, typecmd + excmd, num=8)

            typecmd = f" AND subject_type = {2} "
            df2 = _query2df(uid, typecmd + excmd, num=2)

        if len(df1) == 0:
            return df2
        elif len(df2) == 0:
            return df1
        else:
            df = pd.concat([df1, df2]).sort_values(by="timestamp", ascending = False)

    elif type_ == 3:
        if InCollects:
            search_types = [2,3,4,6]
            ddf_ = ddf[ddf["subject_type"].isin(search_types)]
            df = ddf_.iloc[:num]
        else:
            typecmd = f" AND subject_type in (2,3,4,6) "
            df = _query2df(uid, typecmd + excmd)

    else:
        if InCollects:
            df = ddf.iloc[:num]
        else:
            typecmd = " AND TRUE "
            df = _query2df(uid, typecmd + excmd)

    return df

def _query2df(uid, typecmd, num=10):
    conn, cursor = connect_sql(dict = 1)
    query = f"""
            SELECT * 
            FROM collect 
            WHERE uid = {uid}
            AND type IN (2) 
            AND (rate >= 5 OR rate = 0) 
            {typecmd}
            ORDER BY `datetime_temp` DESC
            LIMIT {num};
            """
    cursor.execute(query)
    res = cursor.fetchall()
    if res:
        df = pd.DataFrame(res)
        return df
    else:
        return []

