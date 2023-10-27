import pandas as pd
import time
from collections import deque
import numpy as np
from src.sql.connect import connect_sql

class User:
    def __init__(self) -> None:
        self.data_ir = None

        self.uid = None
        self.sys_index = None
        self.uname = None
        
        self.local_update_time = {
            1:0,
            2:0,
            3:0,
            4:0,
            6:0,
        }

        self.tem_collecting_maxtime = {i:0 for i in [1,2,3,4,6]}

        ## 记录query时间信息
        self.query_time_record = deque(maxlen=1000)

    @property
    def local_update_time_date(self):
        return {i:pd.Timestamp(self.local_update_time[i], unit="s").tz_localize('UTC').tz_convert('Asia/Shanghai') for i in [1,2,3,4,6]}

    def __lt__(self, other):
        return score(self) < score(other)
    
    def receive_query(self):
        self.query_time_record.append(time.time())

    @property
    def last_query_time(self):
        if len(self.query_time_record) == 0:
            return 0
        else:
            return self.query_time_record[-1]

    @property
    def total_queries_last_month(self):
        t = time.time()
        tgap = t - np.array(self.query_time_record)
        num = (tgap <= 30*24*3600).sum()
        return num

    def total_records(self, days):
        days = int(days)
        t = time.time()
        lastm = t - days * 24 * 3600
        connection, cursor = connect_sql()
        query = ("SELECT COUNT(*) FROM collect WHERE uid = %s AND timestamp > %s")
        cursor.execute(query, (self.uid, lastm))
        count = cursor.fetchone()[0]
        return count

    @property
    def total_records_last_month(self):
        return self.total_records(days=30)

def score(cls):
    return (cls.total_queries_last_month + 1) * cls.total_records_last_month

import heapq

class ActiveUserList:
    def __init__(self, max_size):
        self.queue = []
        self.max_size = max_size

    def push(self, user):
        if score(user) == 0:
            pass
        else:
            if len(self.queue) < self.max_size:
                heapq.heappush(self.queue, user)
            else:
                # 如果新元素的优先级高于当前最低优先级的元素，则替换
                heapq.heappushpop(self.queue, user)

    def uid_list(self):
        return [e.uid for e in self.queue]
    
