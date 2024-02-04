from src.sql.connect import connect_sql
import pandas as pd
from src.graphdata.neo4j_f import GraphDB
from src.sql.query_f import query_max_sid

def _get_candidate_list():
    query = "SELECT sid FROM candidateItem;"
    conn, cursor = connect_sql()
    cursor.execute(query)
    res = cursor.fetchall()
    sid_list = [i[0] for i in res]
    return sid_list


# @profile
def item_filting(para, flag = "0"):
    if flag == "search":
        max_sid = query_max_sid()
        sid_set = set(range(1,max_sid+1))    
    
    else:
        sid_set = set(_get_candidate_list())

    IsTimeFilter = para["IsTimeFilter"]
    IsTagFilter = para["IsTagFilter"]
    type_ = para["type"]

    query = f"SELECT sid FROM candidateItem WHERE (TRUE) "

    if IsTimeFilter:
        st = para["st"]
        et = para["et"]
        
        query += f"AND (`date` > '{st}') AND (`date` < '{et}') "

    if type_ in [1,2,3,4,6]:
        query += f"AND (`subject_type` = {type_}) "

    conn, cursor = connect_sql(dict=1)
    cursor.execute(query)
    try:
        time_sid_set = set(pd.DataFrame(cursor.fetchall()).sid)
    except:
        return []

    sid_set &= time_sid_set

    if IsTagFilter:
        tags = para["tags"]
        tags_sid_set = set(query_tags(tags))
        sid_set &= tags_sid_set

    return list(sid_set)

def query_tags(tags):
    assert len(tags) > 0
    gdb = GraphDB()
    sid_list = gdb.find_subjects_by_tags(tags)    
    return sid_list

def query_dislike_items(uid):
    query = f"SELECT sid FROM feedback_dislike WHERE uid = {uid};"
    conn, cursor = connect_sql()
    cursor.execute(query)
    try:
        res = cursor.fetchall()
        sid_list = [i[0] for i in res]
        return sid_list
    except:
        return []
