## 弃用

from src.sql.connect import connect_sql
import numpy as np
from src.sql.vec_sql.user_vec_database import create_user_or_item_vec_tabel, UserItemVecSql


def create_mf_vec_sql():
    table_name = "MF_User_Vec"
    create_user_or_item_vec_tabel(table_name, col_name="uid")

    table_name = "MF_Item_Vec"
    create_user_or_item_vec_tabel(table_name, col_name="sid")

def store_tensor2sql(table_name, user_or_item_id_list, UoI, col_name):
    vec_sql = UserItemVecSql(table_name)
    UoI = UoI.detach().numpy()
    for id, vec in zip(user_or_item_id_list, UoI):
        vec_sql.insert_or_update(id, vec, col_name)
    
def store_Utensor2sql(uid_list, U):
    store_tensor2sql("MF_User_Vec", uid_list, U, "uid")

def store_Itensor2sql(sid_list, I):
    store_tensor2sql("MF_Item_Vec", sid_list, I, "sid")

