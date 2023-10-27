from src.sql.connect import connect_sql
import pandas as pd

from .F import time_w,tag_similar_weight
from src.utils.F import time_now
import numpy as np

from src.sql.F import get_rec_candidate_list
from src.graphdata.neo4j_f import GraphDB

class TransferMa:
    def __init__(self, table_name = "trans_ma") -> None:
        self.active_items_setting()
        self.sid2date_setting()
        self.table_name = table_name

        self.check_table_exist()

    def check_table_exist(self):
        conn, cursor = connect_sql()
        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{self.table_name}';")
        if cursor.fetchone() is None:
            # Create table if it doesn't exist
            cursor.execute(f"CREATE TABLE {self.table_name} LIKE trans_ma;")
        
        conn.commit()
        cursor.close()
        conn.close()        

    def active_items_setting(self):
        # query = "SELECT sid FROM item_info WHERE (`rank` > 0) AND (`date` IS NOT NULL) AND (locked = 0);"
        # conn, cursor = connect_sql()
        # cursor.execute(query)
        # res = cursor.fetchall()
        # self.sid_list = [i[0] for i in res]

        self.sid_list = get_rec_candidate_list()

        num = len(self.sid_list)
        self.sid2index = {sid:i for sid,i in zip(self.sid_list, range(num))}
        self.index2sid = {i:sid for sid,i in zip(self.sid_list, range(num))}
        

    def sid2date_setting(self):
        query = f"SELECT sid, date, eps, platform, nsfw, `type` FROM item_info;"
        conn, cursor = connect_sql(dict=1)
        cursor.execute(query)
        res = cursor.fetchall()
        df_ = pd.DataFrame(res)
        
        df_ = df_[~df_.date.isna()]

        df_.date = df_.date.apply(lambda x: pd.Timestamp(x).timestamp())
        dd = {sid:date for sid,date in zip(df_.sid, df_.date)}
        self.sid2date = dd

        self.sid2eps = {sid:date for sid,date in zip(df_.sid, df_.eps)}
        self.sid2type = {sid:int(t) for sid,t in zip(df_.sid, df_["type"])}
        self.sid2nsfw = {sid:n for sid,n in zip(df_.sid, df_.nsfw)}
        self.sid2platform = {sid:n for sid,n in zip(df_.sid, df_.platform)}


        query = f"SELECT * FROM item_pop_stat"
        cursor.execute(query)
        df_pop_stat = pd.DataFrame(cursor.fetchall())

        self.pop_stat_d = {}
        cols = list(df_pop_stat.columns)
        cols.remove("nsfw")
        cols.remove("subject_type")
        for i,r in df_pop_stat.iterrows():
            self.pop_stat_d[(r.subject_type, r.nsfw)] = {col:r[col] for col in cols}

        self.sid2effectiveTag_dict = {} 
        gb = GraphDB()
        print("querying effectiveTag")
        num = 0
        for sid in self.sid_list:
            num += 1
            self.sid2effectiveTag_dict[sid] = gb.get_effectiveTag(sid)
            if num % 2000 == 0:
                print(f"{num=} / {len(self.sid_list)}")
        print("finish effectiveTag")

    def compute_trans(self):
        print("query uid list")
        query = f"SELECT DISTINCT(uid) FROM collect;"
        conn, cursor = connect_sql()
        cursor.execute(query)
        res = cursor.fetchall()
        uid_list = [i[0] for i in res]

        num = 0
        for uid in uid_list[num:]:
            num += 1
            self.compute_trans_by_user(uid)
            if num % 10 == 0:
                print(f"num = {num}/{len(uid_list)}, {time_now()=}")

    # @profile
    def compute_trans_by_user(self, uid):
        query = f"SELECT * FROM collect WHERE uid = {uid};"
        conn, cursor = connect_sql(dict=1)
        cursor.execute(query)
        res = cursor.fetchall()


        df_0 = pd.DataFrame(res).sort_values(by="timestamp")
        df_0 = df_0[df_0.sid.isin(self.sid_list)]

        groups = df_0.groupby(np.arange(len(df_0)) // 500)
        conn, cursor = connect_sql()

        

        for name, df in groups:
            for i,(i_,row) in enumerate(df.iterrows()):
                """
                即使是当前状态被抛弃的番剧，仍然计算在内
                """
                sid = row.sid

                subject_tag = self.sid2effectiveTag_dict[sid]
                
                item_collect_time = row.timestamp
                rel_df = df.iloc[i + 1: i + 11 ]
                
                item_date = self.sid2date[sid]
                sid_eps = self.sid2eps[sid]

                

                i_start = item_date
                sp = self.sid2platform[sid]
                subejct_type = self.sid2type[sid]

                i_end = _set_end_time(sp, i_start, sid_eps,  subejct_type)

                for j,rel_row in rel_df.iterrows():
                    rel_sid = rel_row.sid
                    rel_timestamp = rel_row.timestamp
                    subejct_type_ = self.sid2type[rel_sid]
                    n_ = self.sid2nsfw[rel_sid]                    

                    ## 基础分数
                    type_ = rel_row["type"]
                    rate =  rel_row["rate"]

                    if type_ == 1:
                        s = 0.2
                    elif type_ == 2:
                        if rate >= 7:
                            s = 1
                        elif rate >= 5:
                            s = 0.5
                        elif rate == 0:
                            s = 0.5
                        elif 1<=rate <= 4:
                            s = -1
                    elif type_ == 3:
                        s = 0
                        continue
                        # if rate >= 7:
                        #     s = 0.7
                        # else:
                        #     s = 0.3
                    elif type_ == 4:
                        if 1 <=rate <= 4:
                            s = -1
                        else:
                            s = -0.3
                    elif type_ == 5:
                        s = -1

                    # 时间降权
                    w_t = time_w(item_collect_time, rel_timestamp)
                    if w_t == 0:
                        continue


                    # tag调整权重
                    rel_subject_tag = self.sid2effectiveTag_dict[rel_sid] 
                    # gb.get_effectiveTag(rel_sid)
                    w_tag = tag_similar_weight(subject_tag, rel_subject_tag)

                    if w_tag == 0:
                        continue


                    # 相近季度降权
                    rel_item_date = self.sid2date[rel_sid]
                    relsid_eps = self.sid2eps[rel_sid]
                    relsp = self.sid2platform[rel_sid]                    
                                        
                    rel_start = rel_item_date
                    rel_end = _set_end_time(relsp, rel_start, relsid_eps, subejct_type_)


                    tt = abs(rel_start - i_start)/(3600*24*30)
                    tt2 = abs(rel_end - i_end)/(3600*24*30)
                    if tt <= 3:
                        w_0 = 0
                        continue
                    elif tt2 <= 3:
                        w_0 = 0
                        continue
                    elif relsp == "剧场版" or sp == "剧场版":
                        if 3 <= tt2 <= 12:
                            w_0 = 0.1
                        else:
                            w_0 = 1
                    elif 3 <= tt2 <= 6:
                        w_0 = 0.1
                    else:
                        w_0 = 1
                    
                    
                    ## 热门作品降权
                    ymf = timestamp2YM(rel_timestamp)
                    
                    # total_pop = self.pop_stat_d[(subejct_type_, n_)][ymf]                                
                    query = f"SELECT `{ymf}` FROM item_pop WHERE sid = {rel_sid}"
                    cursor.execute(query)
                    res = cursor.fetchall()[0][0]
                    if res <= 100:
                        w_pop = 1
                    else:
                        # w_pop = min(1, total_pop/1000/res)
                        w_pop = min(1, 100/res)
                    
                    
                    score = w_tag * w_0 * w_t * w_pop * s
                    if score == 0:
                        continue
                    
                    query = f"""
                        INSERT INTO {self.table_name} (sid, trans_sid, trans_score)
                        VALUES ({sid}, {rel_sid}, {score})
                        ON DUPLICATE KEY UPDATE trans_score = trans_score + {score};
                    """
                    cursor.execute(query)
        conn.commit()
                

# from pympler.asizeof import asizeof

from datetime import datetime

def timestamp2YM(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    year = dt_object.strftime('%y')
    month = int(dt_object.strftime('%m'))
    
    # 调整月份
    if month <= 3:
        adjusted_month = '01'
    elif month <= 6:
        adjusted_month = '04'
    elif month <= 9:
        adjusted_month = '07'
    else:
        adjusted_month = '10'
    
    return year + adjusted_month + "~"

def _set_end_time(sp, item_date, sid_eps, subject_type):
    oneday_t = 3600*24

    if sp == "TV":
        iend = item_date + sid_eps * 7 * oneday_t
    elif sp == "OVA":
        iend = item_date
    elif sp == "剧场版":
        iend = item_date + 365 * oneday_t
    elif subject_type == 6:
        iend = item_date + sid_eps * 7 * oneday_t
    else:
        iend = item_date
    return iend
