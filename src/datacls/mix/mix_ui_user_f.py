from src.data_spider_mysql.ui_ir_f import run_spider,insert_into_collect
from src.sql.connect import connect_sql
import pandas as pd
import time

class MixUiUser:
    # 更新大概需要50 min
    def update_active_user_list(self):
        # self._active_user_list
        connection,cursor = connect_sql()

        query = ("SELECT DISTINCT uid FROM collect")
        cursor.execute(query)
        unique_uids = [row[0] for row in cursor.fetchall()]
        print(f"total rounds = {len(unique_uids)}")

        num = 0
        for uid in unique_uids:
            num += 1
            user = self.get_user(uid)
            self._active_user_list.push(user)
            if num % 100 == 0:
                print(f"round = {num}, active user deciding, {uid=}")

            if num > 4000:
                break
