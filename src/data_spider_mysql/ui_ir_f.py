
import pandas as pd
import re
from src.AsycSpider import Spider
from src.sql.connect import connect_sql


def extract_values_from_url(url):
    # 使用正则表达式提取uname, type, offset
    uname_pattern = r"/users/(\w+)/collections"
    type_pattern = r"subject_type=(\w+)"
    offset_pattern = r"offset=(\d+)"

    uname = re.search(uname_pattern, url)
    type_ = re.search(type_pattern, url)
    offset = re.search(offset_pattern, url)

    return {
        'uname': uname.group(1) if uname else None,
        'type': type_.group(1) if type_ else None,
        'offset': offset.group(1) if offset else None
    }

def f(rawdata):
    if len(rawdata) == 0:
        return {"df":pd.DataFrame([])}
    
    url = rawdata["url"]
    values_d = extract_values_from_url(url)

    data = {}

    data["uname"] = values_d['uname']
    data["type"] = int(values_d['type'])
    data["offset"] = int(values_d['offset'])

    if "data" in rawdata.keys():
        df = pd.DataFrame(rawdata["data"])
        if len(df) != 0:
            df["sid"] = [s["id"] for s in df["subject"] ]
            df["timestamp"] = [pd.Timestamp(t, unit="s").timestamp() for t in df["updated_at"]]
            list_ = ["sid", "rate", "type", "timestamp", "subject_type"]
            df = df[list_]
        
        data["df"] = df    
    else:
        data["df"] = pd.DataFrame([])
        data["description"] = rawdata.get("description", None)
    
    return data

def insert_into_collect(uid, sid, rate, type_, st, timestamp, datetime_temp):
    connection, cursor = connect_sql()
    
    # 使用INSERT ... ON DUPLICATE KEY UPDATE语句
    query = """
    INSERT INTO collect(uid, sid, rate, type, subject_type, timestamp, datetime_temp)
    VALUES(%s, %s, %s, %s, %s, %s, %s) AS new_values
    ON DUPLICATE KEY UPDATE
        rate = new_values.rate,
        type = new_values.type,
        subject_type = new_values.subject_type,
        timestamp = new_values.timestamp,
        datetime_temp = new_values.datetime_temp
    """    
    cursor.execute(query, (uid, sid, rate, type_, st, timestamp, datetime_temp))

    connection.commit()  
    cursor.close()



def run_spider(collect_info_set):
    urls = [
        f"https://api.bgm.tv/v0/users/{user_name}/collections?subject_type={type}&limit=50&offset={offset}" \
            for uid, user_name, type, offset in collect_info_set
            ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    s = Spider(f, headers=headers)
    items = s.run(urls)

    return items
