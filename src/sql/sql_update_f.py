from src.sql.connect import connect_sql
from src.utils.F import get_midnight_timestamp
import time
import pandas as pd
from src.data_spider_mysql.item_info_f import run_spider
import numpy as np
from src.datacls.ui_f import UI_cls

class UpdateSQL:
    """
        item 的维护, user collect 维护，每天维护
    """
    def __init__(self) -> None:
        pass

    def update_item_info(self, days = 1):
        """
            只维护新数据，不维护旧数据
        """
        t = time.time()
        t = int(get_midnight_timestamp(t)) 

        matained_earliest_time = t - 365*24*3600
        matained_earliest_time = pd.Timestamp(matained_earliest_time, unit="s")

        new_data_earliest_time = t - 24 * 3600 * days

        connection, cursor = connect_sql()
        query = "SELECT DISTINCT sid FROM collect WHERE timestamp > %s"
        cursor.execute(query, (new_data_earliest_time,)) 

        result = cursor.fetchall()
        sid_set = set([ r[0] for r in result])

        query_item = "SELECT sid FROM item_info WHERE date > %s OR date IS NULL"
        cursor.execute(query_item, (matained_earliest_time,) )
        result_item = cursor.fetchall()
        
        update_item_candidate_set = set([r[0] for r in result_item])

        update_item_list = list(update_item_candidate_set & sid_set)

        urls = [
            f"https://api.bgm.tv/v0/subjects/{sid}" for sid in update_item_list
        ]
        run_spider(urls)

    def update_collect_random_user(self):
        """
            不实现新用户更新，用户手动使用系统则有可能可以更新
        """
        t = time.time()
        t = get_midnight_timestamp(t)
        matained_earliest_time = int(t) - 180*24*3600
        query = "SELECT uid FROM collect WHERE timestamp > %s"

        connection, cursor = connect_sql()
        cursor.execute(query, (matained_earliest_time,)) 
        result = cursor.fetchall()

        uid_list = list(set([ r[0] for r in result]))
        update_uid_list = np.random.choice(uid_list, size = 10000, replace=False)
        
        ui_cls = UI_cls()
        ui_cls.update_collect_table(update_uid_list)
