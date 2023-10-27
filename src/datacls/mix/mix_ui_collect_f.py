from src.data_spider_mysql.ui_ir_f import run_spider,insert_into_collect
from src.sql.connect import connect_sql
import pandas as pd
import time

class MixUiCollect:
    def process_items(self, items):

        def insert2sql(_df, uid):
            for i,r in _df.iterrows():
                datetime_temp = pd.Timestamp(r.timestamp, unit="s").tz_localize('UTC').tz_convert('Asia/Shanghai')
                insert_into_collect(uid, r.sid, r.rate, r.type, r.subject_type, r.timestamp, datetime_temp)

        collect_info_set = []

        for item in items:
            df = item.df
            
            if len(df) == 0:
                continue

            uname = item.uname
            offset = item.offset
            connection, cursor = connect_sql()
            
            # 查询user_mapping表以获取与uname对应的uid
            query = f"SELECT uid FROM user_mapping WHERE `uname` = '{uname}'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                uid = result[0]
                # 这里你可以继续进行其他操作，如使用uid进行进一步的操作或存储
            else:
                continue

            cursor.close()    

            user = self.get_user(uid)
            t = item.type
            last_touch_time = user.local_update_time[t]

            min_time = df.timestamp.min()
            max_time = df.timestamp.max()

            if user.tem_collecting_maxtime[t] == 0:
                if max_time <= last_touch_time:
                    continue
                elif min_time <= last_touch_time < max_time:
                    new_dft = df[df.timestamp > last_touch_time]

                    insert2sql(new_dft, uid)                    
                    user.local_update_time[t] = max_time
                
                else:                                        
                    user.tem_collecting_maxtime[t] = max_time
                    insert2sql(df, uid)    
                    if len(df) == 50:
                        collect_info_set.append((uid, uname, t, offset + 50))                
                    
            else:
                assert offset != 0
                if max_time <= last_touch_time:
                    user.local_update_time[t] = user.tem_collecting_maxtime[t]
                    user.tem_collecting_maxtime[t] = 0

                elif min_time <= last_touch_time < max_time:
                    new_dft = df[df.timestamp > last_touch_time]
                    
                    insert2sql(new_dft, uid)
                    user.local_update_time[t] = user.tem_collecting_maxtime[t]
                    user.tem_collecting_maxtime[t] = 0

                else:                    
                    insert2sql(df, uid)
                    if len(df) == 50:
                        collect_info_set.append((uid, uname, t, offset + 50))
        return collect_info_set                    


    def update_collect_table_spider(self, collect_info_set):
        batch = 500
        rounds = len(collect_info_set) // batch
        print(f"{batch = }, total rounds = {rounds + 1}")
        re_c_info_set = []
        for i in range(rounds + 1):
            t = time.time()
            t = pd.Timestamp(t, unit="s").tz_localize('UTC').tz_convert('Asia/Shanghai')
            print(f"round = {i} / {rounds}, {t = }")
            min_ = i * batch
            max_ = min(len(collect_info_set), (i+1) * batch)
            list_ = collect_info_set[min_:max_]
            if len(list_) == 0:
                continue
            items = run_spider(list_) 
            re_c_info_set += self.process_items(items)
        return re_c_info_set

