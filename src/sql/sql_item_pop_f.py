import pandas as pd
from src.sql.connect import connect_sql

def airflow_update_sql_item_pop():
    """
    TODO: 扩列的需求
    """
    conn, cursor = connect_sql(dict=1)
    cursor.execute("SELECT DISTINCT(sid) FROM collect")
    s1 = set(pd.DataFrame(cursor.fetchall()).sid)

    cursor.execute("SELECT DISTINCT(sid) FROM item_info")
    s2 = set(pd.DataFrame(cursor.fetchall()).sid)

    sid_list = list(s1&s2)

    # num = 0
    num = 180000
    for sid in sid_list[num:]:
        num += 1
        try:
            df = _get_item_interaction(sid)
            popularity = _calculate_popularity(df)
            update_item_pop(sid, popularity)    
        except:
            print(f"failed {sid = }")

        if num % 100 == 0:
            print(f"{num=}")

def airflow_update_sql_item_pop_stat():
    tn_ = [(t,n) for t in [1,2,3,4,6] for n in [0,1]]
    # tn_.remove((1,0))
    # tn_.remove((3,0))
    quarters = ["01~", "04~", "07~", "10~"]
    column_names = []
    start_year = 2008
    end_year = 2024

    for year in range(start_year, end_year + 1):
        for quarter in quarters:
            column_names.append(f'{str(year)[2:]}{quarter}')


    for subject_type, nsfw in tn_:
        conn,cursor = connect_sql(dict=1)
        query = f"SELECT sid FROM item_info WHERE type = {subject_type} AND nsfw = {nsfw}"
        cursor.execute(query)
        
        sidlist = list(pd.DataFrame(cursor.fetchall()).sid)        
        
        cc = [f"`{c}`" for c in column_names]

        query = f"""
        INSERT INTO item_pop_stat (subject_type, nsfw) VALUES ({subject_type}, {nsfw})
        ON DUPLICATE KEY UPDATE subject_type = {subject_type}, nsfw = {nsfw}
        """

        cursor.execute(query)
        conn.commit()

        conn,cursor = connect_sql()

        for col in cc:
            v = 0
            batch = 10000
            rounds =  len(sidlist) // batch + 1
            for i in range(rounds):
                min_ = i*batch
                max_ = min((i+1)*batch, len(sidlist))
                slist = sidlist[min_:max_]
                q1 = f"""
                    SELECT SUM({col}) FROM item_pop WHERE sid IN {tuple(slist)}
                    """
                cursor.execute(q1)
                try:
                    v += int(cursor.fetchall()[0][0])
                except:
                    # print(q1)
                    pass
                    # assert False

            query = f"""
                    UPDATE item_pop_stat
                    SET {col} = {v}
                    WHERE subject_type = {subject_type} AND nsfw = {nsfw}
                    """
            cursor.execute(query)
            conn.commit()



def _get_item_interaction(sid):
    conn, cursor = connect_sql(dict=1)

    query = f"SELECT datetime_temp, uid FROM collect WHERE sid = {sid}"

    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    df['datetime_temp'] = pd.to_datetime(df['datetime_temp'])

    df.set_index('datetime_temp', inplace=True)

    cursor.close()
    conn.close()

    return df

def _calculate_popularity(df):
    start_year = 2008
    end_year = 2024
    quarters = [(1, 3), (4, 6), (7, 9), (10, 12)]
    popularity = {}

    for year in range(start_year, end_year + 1):
        for start_month, end_month in quarters:
            mask = (df.index.year == year) & (df.index.month >= start_month) & (df.index.month <= end_month)
            count = df[mask].shape[0]
            column_name = f"{str(year)[2:]}{str(start_month).zfill(2)}~"
            popularity[column_name] = count

    return popularity

def update_item_pop(sid, popularity):
    conn, cursor = connect_sql()

    columns = ", ".join([f"`{key}`" for key in popularity.keys()])
    values = ", ".join(map(str, popularity.values()))
    update_columns = ", ".join([f"`{key}` = {value}" for key, value in popularity.items()])

    query = f"INSERT INTO item_pop (sid, {columns}) VALUES ({sid}, {values}) ON DUPLICATE KEY UPDATE {update_columns}"

    cursor.execute(query)
    conn.commit()

    cursor.close()
    conn.close()


def generate_column_names(start_year, end_year):
    quarters = ["01~", "04~", "07~", "10~"]
    column_names = []

    for year in range(start_year, end_year + 1):
        for quarter in quarters:
            column_names.append(f'`{str(year)[2:]}{quarter}` INT')

    return column_names

def create_table_pop_stat():    
    conn, cursor = connect_sql()

    # 生成列名
    start_year = 2008
    end_year = 2024
    columns = generate_column_names(start_year, end_year)
    columns_sql = ", ".join(columns)

    # 创建表
    create_table_query = f"""
    CREATE TABLE item_pop_stat (
        subject_type INT,
        nsfw INT,
        {columns_sql}
    );
    """
    cursor.execute(create_table_query)
    print("Table created successfully!")

    # 关闭连接
    cursor.close()
    conn.close()

