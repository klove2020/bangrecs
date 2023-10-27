import aiohttp
import asyncio
token = 'qjUW7T2CxPOC8AN8PjHR40zukQv0NYObZgUBKHur'
import mysql.connector
import pandas as pd

from src.AsycSpider import Spider

def f(rawdata):
    js = rawdata
    item_info = {
        'sid': js.get("id", None),
        'date': js.get("date", None),
        'platform': js.get("platform", None),
        'summary': js.get("summary", None),
        'name': js.get("name", None),
        'name_cn': js.get("name_cn", None),
        'tags': js.get("tags", None),
        'infobox': js.get("infobox", None),
        'rating': js.get("rating", None),
        'total_episodes': js.get("total_episodes", None),
        'collection': js.get("collection", None),
        'eps': js.get("eps", None),
        'volumes': js.get("volumes", None),
        'locked': js.get("locked", None),
        'nsfw': js.get("nsfw", None),
        'type': js.get("type", None),
        'images': js.get("images", None),
    }

    
    rating_data = item_info['rating']
    if type(rating_data) == type(None):
        rating_data = {}

    item_info['rank'] = rating_data.get('rank', None)
    item_info['total']= rating_data.get('total', None)
    item_info['count'] = json.dumps(rating_data.get('count', None), ensure_ascii=False)
    item_info['score']= rating_data.get('score', None)

    for field in ["infobox", "collection","images", "tags"]:
        v = item_info[field]
        if type(v) != type(None):
            item_info[field] = json.dumps(v, ensure_ascii=False)
    
    del item_info["rating"]
    return item_info


import json

def _run_spider(urls=[]):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    max_concurrent = 20
    s = Spider(f, data_format="json", headers=headers, max_concurrent=max_concurrent)
    items = s.run(urls)
    save_to_mysql(items)

def run_spider(urls=[]):
    batch = 500
    rounds = len(urls) // batch
    print(f"{batch = }, total rounds = {rounds + 1}")
    for i in range(rounds + 1):
        t = time.time()
        t = pd.Timestamp(t, unit="s").tz_localize('UTC').tz_convert('Asia/Shanghai')
        print(f"round = {i} / {rounds}, {t = }")
        min_ = i * batch
        max_ = min(len(urls), (i+1) * batch)
        list_ = urls[min_:max_]
        if len(list_) == 0:
            continue
        _run_spider(list_)
    


def save_to_mysql(items):
    config = {
        'user': 'root',
        'password': 'abc159753',
        'host': 'localhost',
        'database': 'bangumi',
        'raise_on_warnings': True
    }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Check and create table if not exists
    create_table_if_not_exists(cursor)


    add_item = """
    INSERT INTO item_info  
    (sid, `date`, platform, summary, name, name_cn, tags, infobox, `rank`, `total`, `count`, score, 
    total_episodes, collection, eps, volumes, locked, nsfw, 
    `type`, images) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS new
    ON DUPLICATE KEY UPDATE 
    `date` = new.`date`, 
    platform = new.platform, 
    summary = new.summary, 
    name = new.name, 
    name_cn = new.name_cn, 
    tags = new.tags, 
    infobox = new.infobox, 
    `rank` = new.`rank`, 
    `total` = new.`total`, 
    `count` = new.`count`, 
    score = new.score, 
    total_episodes = new.total_episodes, 
    collection = new.collection, 
    eps = new.eps, 
    volumes = new.volumes, 
    locked = new.locked, 
    nsfw = new.nsfw, 
    `type` = new.`type`, 
    images = new.images;
"""

    for item in items:
        if item.sid is None:  # Check if sid is None
            print("Warning: Missing 'sid' for an item. Skipping...")
            continue  # Skip this item

        data_item = (
            item.sid, item.date, item.platform, item.summary, item.name, item.name_cn,
            item.tags, item.infobox, item.rank, item.total, item.count, item.score, item.total_episodes, 
            item.collection, item.eps, item.volumes, item.locked, item.nsfw, item.type, item.images
        )
        # print(data_item)
        try:
            cursor.execute(add_item, data_item)
        except:
            continue
        
    connection.commit()
    cursor.close()
    connection.close()


import time
def create_table_if_not_exists(cursor):
    # Check if table exists
    cursor.execute("SHOW TABLES LIKE 'item_info'")
    result = cursor.fetchone()
    
    # If table doesn't exist, create it
    if not result:
        create_table_query = """
        CREATE TABLE item_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sid VARCHAR(255) NOT NULL,
            `date` DATE,
            platform VARCHAR(255),
            summary TEXT,
            name VARCHAR(255),
            name_cn VARCHAR(255),
            tags JSON,
            infobox JSON,
            `rank` INT,
            `total` INT,
            `count` JSON,
            score FLOAT,
            total_episodes INT,
            collection JSON,
            eps INT,
            volumes INT,
            locked BOOLEAN,
            nsfw BOOLEAN,
            `type` VARCHAR(255),
            images JSON
        )
        """
        cursor.execute(create_table_query)

