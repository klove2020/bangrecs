import pandas as pd
from src.utils.save import save_class, load_class
from src.datacls.user_f import User, ActiveUserList
from src.sql.connect import connect_sql

from src.data_spider_mysql.user_mapping_f import collect_one_user_name, update_sql_by_uid

from src.datacls.mix.mix_ui_user_f import MixUiUser
from src.datacls.mix.mix_ui_local_time_f import MixUiLocalTime
from src.datacls.mix.mix_ui_attri_f import MixUiAttri
from src.datacls.mix.mix_ui_rec_f import MixUiRec
from src.datacls.mix.mix_ui_collect_f import MixUiCollect
import time

class UI_cls(MixUiUser, MixUiLocalTime, MixUiRec, MixUiAttri, MixUiCollect):
    def __init__(self) -> None:
        self.save_path = "data/database"
        self.user_total_nums = None        
        self.user_dict = {}
        self.item_dict = {}
        self._active_user_list = ActiveUserList(max_size=2000)
        self.fetch_user_map()


    @property
    def active_user_list(self):
        return self._active_user_list.uid_list()

                
    def update_collect_table_active_user(self):
        uid_list = self.active_user_list
        self.update_collect_table(uid_list)

    def update_collect_table(self, uid_list):    
        self.update_user_local_time(uid_list)    
        
        d = self.uid_to_uname
        uname_list = [d.get(uid, uid) for uid in uid_list]                
        collect_info_set = [(uid, uname, type, o) for uid,uname in zip(uid_list,uname_list) for type in [1,2,3,4,6] for o in [0] ]
        self._update_collect_table_by_user(collect_info_set)

    # @profile
    def update_collect_table_one_user(self, uid, update_f = False):
        u = self.get_user(uid)
        if sum(u.local_update_time.values()) == 0:
            self.matain_single_user_loacl_time(uid)
        t = time.time()

        connection, cursor = connect_sql()
        cursor.execute(f'SELECT uname FROM user_mapping WHERE `uid` = {uid}')        
        nn_ = cursor.fetchall()
        
        if not nn_:
            print("No records found.")
            uname = self.update_user_mapping_by_uid(uid)
            assert uname != None            
        else:
            uname = nn_[0][0]

        collect_info_set = [(uid, uname, type, o) for type in [1,2,3,4,6] for o in [0] ]
        print(f"{update_f=}")
        if update_f:
            self._update_collect_table_by_user(collect_info_set)
        else:
            last_time = max(max(u.local_update_time.values()), u.last_query_time)
            now = time.time()
            if now - last_time < 3600 * 24:
                pass
            else:
                self._update_collect_table_by_user(collect_info_set)

    def _update_collect_table_by_user(self, collect_info_set):
        r = 0
        while len(collect_info_set) > 0: 
            r += 1
            print(f"round {r}, requesting api nums = {len(collect_info_set)}")
            collect_info_set = self.update_collect_table_spider(collect_info_set)


    def update_user_mapping_by_uid(self, uid):
        uname = update_sql_by_uid(uid)
        return uname

    def save_cls(self):
        save_class(self, f"{self.save_path}/ui_cls.cls")

            