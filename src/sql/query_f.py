from src.sql.connect import connect_sql
import pandas as pd

def query_uid(uname):
    query = """
    SELECT uid from user_mapping WHERE `uname` = %s;
    """
    conection, cursor = connect_sql()
    cursor.execute(query, (uname,))
    r = cursor.fetchall()
    if r:
        return r[0][0]
    else:
        return None

def query_max_uid():
    conection, cursor = connect_sql()
    cursor.execute("SELECT MAX(uid) FROM collect")
    r = cursor.fetchone()
    return r[0]

def query_max_sid():
    conn, cursor = connect_sql()
    query = "SELECT MAX(sid) FROM item_info;"
    cursor.execute(query)
    max_sid = cursor.fetchone()[0]
    return max_sid

def query_item_info_by_sidlist(sid_list):

    assert len(sid_list) > 0
    connection, cursor = connect_sql(dict=1)

    if len(sid_list) == 1:
        sidlistcmd = f"sid = {sid_list[0]}"
    else:
        sidlistcmd = f"sid in {tuple(sid_list)}"

    query = f"""
        SELECT 
            `type` AS subject_type,
            sid,
            date,
            summary,
            name,
            name_cn,
            `rank`,
            score,
            nsfw,
            images ->>'$.medium' AS image_medium
        FROM item_info 
        WHERE {sidlistcmd}
        """
    cursor.execute(query)
    results = cursor.fetchall()

    return results

def get_effectivetags_list():
    connection, cursor = connect_sql(dict=1)
    query = f"SELECT tag FROM _cache_tags_list"
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    return list(df.tag)
    
