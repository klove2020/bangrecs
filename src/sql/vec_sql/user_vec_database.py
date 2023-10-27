from src.sql.vec_sql.base import *


def create_user_or_item_vec_tabel(tn, col_name):
    assert col_name in ["uid", "sid"]
    conn, cursor = connect_sql()
    if tn in ["TEST_user_vec_mf"]:
        try:
            q = f"DROP TABLE {tn};"
            cursor.execute(q)
        except:
            pass

    if col_name == "uid":
        index_col_name = "u_index"
        create_table(tn, index_col_name, "uid INT NOT NULL,")        
        q = f"ALTER TABLE {tn} ADD UNIQUE (uid);"
        cursor.execute(q)
    
    elif col_name == "sid":
        index_col_name = "s_index"
        create_table(tn, index_col_name, "sid INT NOT NULL,")        
        q = f"ALTER TABLE {tn} ADD UNIQUE (sid);"
        cursor.execute(q)


    # q = f"ALTER TABLE {tn} AUTO_INCREMENT = 0;"
    # cursor.execute(q)


class UserItemVecSql(VectorSql):
    def __init__(self, vecsql_name) -> None:
        super().__init__(vecsql_name)        

    def insert_or_update(self, uOsid:int, vector:np.array, col_name):
        """
        如果数据库中没有此uid, 则插入新的uid和向量。
        如果数据库中已经存在此uid, 则更新其向量。
        """
        conn, cursor = connect_sql()
        vector_bytes = vector.tobytes()

        assert col_name in ["uid", "sid"]

        sql = f"""
        INSERT INTO {self.tn} ({col_name}, vec) 
        VALUES (%s, _binary%s)
        ON DUPLICATE KEY UPDATE vec=_binary%s
        """

        cursor.execute(sql, (uOsid, vector_bytes, vector_bytes))
        conn.commit()
        cursor.close()
        conn.close()

