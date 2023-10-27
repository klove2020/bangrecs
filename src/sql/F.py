from src.sql.connect import connect_sql
import pandas as pd

from src.graphdata.neo4j_f import GraphDB

def get_rec_candidate_list():
    query = "SELECT sid FROM item_info WHERE (`rank` > 0) AND (`date` IS NOT NULL) AND (locked = 0);"
    conn, cursor = connect_sql()
    cursor.execute(query)
    res = cursor.fetchall()
    
    sid_list = [i[0] for i in res]
    gb = GraphDB()
    sid2_list = gb.query_sid_hastags()

    s = set(sid_list) & set(sid2_list)
    return list(s)



def quick_filting_predata():
    sid_list = get_rec_candidate_list()

    connection, cursor = connect_sql(dict=1)


    batchsize = 1000

    round = len(sid_list) // batchsize + 1

    dfl = []
    for i in range(round):
        min_ = i*batchsize
        max_ = min((i+1)*batchsize, len(sid_list))
        sid_list_i = sid_list[min_:max_]

        placeholders = ', '.join(['%s'] * len(sid_list_i))  # 创建占位符字符串         
        query = f"""
        SELECT 
            type AS subject_type, 
            sid, 
            date,
            `rank`,
            score,
            nsfw
        FROM item_info WHERE sid IN ({placeholders});
        """ 
        cursor.execute(query, sid_list_i)    
        dfi = pd.DataFrame(cursor.fetchall())
        dfl.append(dfi)

    df = pd.concat(dfl)
    df.date = df.date.apply(lambda x:pd.Timestamp(x))
    df.subject_type = df.subject_type.astype(int)
    return df

import pandas as pd
from sqlalchemy import create_engine

def writ2sql():
    df = quick_filting_predata()
    # 创建数据库连接
    engine = create_engine("mysql+pymysql://root:abc159753@localhost/bangumi")
    # 将DataFrame写入新的SQL表
    df.to_sql('candidateItem', con=engine, index=False, if_exists='replace')

if __name__ == "__mian__":
    writ2sql()