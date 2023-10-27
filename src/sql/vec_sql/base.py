from src.sql.connect import connect_sql
import numpy as np


def create_table(table_name, index_col_name, other_col_sql_cmd=""):
    """
    默认用vec来表示vec列

    example:
        create_table( "user_vec_mf", "u_index", "uid INT NOT NULL,")
    """
    conn, cursor  = connect_sql()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {index_col_name} INT AUTO_INCREMENT PRIMARY KEY,
        {other_col_sql_cmd}
        vec BLOB
    )
    """)

def auto_find_index_name(tabel_name):
    query = f"""
    SELECT COLUMN_NAME 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'bangumi' 
    AND TABLE_NAME = "{tabel_name}"
    AND EXTRA = 'auto_increment' 
    """
    conn, cursor  = connect_sql()
    cursor.execute(query)
    res = cursor.fetchall()
    return res[0][0]


class VectorSql:
    def __init__(self, vecsql_name) -> None:
        self.tn = vecsql_name
        self.index_col_name = auto_find_index_name(self.tn)

    # 重载get item,self[L] 即调用 self.index
    def __getitem__(self, indices):
        return self.index(indices)

    def exec_sql_cmd(self, cmd):
        conn, cursor = connect_sql()
        cursor.execute(cmd)

    def index(self, L):
        """
        L为行索引值,根据行索引,从数据库中找到相应的行,返回结果并且包装给numpy数组
        """
        
        if type(L) == type(1):
            NL = np.array([L], dtype=int) + 1
        
        elif type(L) == type([]):
            NL = np.array(L, dtype=int) + 1
        else:
            assert False



        conn, cursor  = connect_sql()
        # Convert list L to string format for SQL query
        indices_str = ", ".join(map(str, NL))
        # SQL query to get vectors by indices
        query = f"""
        SELECT vec 
        FROM {self.tn}
        WHERE {self.index_col_name} IN ({indices_str})
        """
        cursor.execute(query)
        # Retrieve all vectors and convert to numpy arrays
        result_vectors = [np.frombuffer(row[0], dtype=float) for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if type(L) == type(1):
            return result_vectors[0]
        elif type(L) == type([1]):
            return np.array(result_vectors)
        else:
            assert False
