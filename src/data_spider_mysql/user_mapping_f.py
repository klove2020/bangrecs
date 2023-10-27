import requests
from bs4 import BeautifulSoup
import re
from src.sql.connect import connect_sql

def collect_one_user_name(uid):
    try:
        url = f"https://bangumi.tv/user/{uid}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',}
        response = requests.get(url, headers= headers)

        if response.status_code == 200:
            uname = response.url.split('/')[-1]
        else:
            uname = uid
        return uname

    except:
        return None

# <span class="avatarNeue avatarSize100" style="background-image:url('//lain.bgm.tv/pic/user/c/000/00/00/1.jpg?r=1671687974&amp;hd=1')"></span>
def collect_uname2uid(uname):
    try:
        url = f"https://bangumi.tv/user/{uname}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',}
        response = requests.get(url, headers= headers)
        bs = BeautifulSoup(response.text)
        uidinfo = bs.find('span', class_='avatarNeue avatarSize100')
        url = uidinfo['style'].split('url(')[-1].split(')')[0].strip("'\"")
        match = re.search(r'/(\d+)\.jpg', url)
        data_id = int(match.group(1))
        return data_id
    
    except:
        return None
    
def update_sql_by_uname(uname):
    uid = collect_uname2uid(uname)

    connection, cursor = connect_sql()
    if type(uid) != type(None):
        query = "INSERT INTO user_mapping (uid, uname) VALUES (%s, %s) AS new ON DUPLICATE KEY UPDATE uid = new.uid"
        cursor.execute(query, (uid, uname))
        connection.commit()
    cursor.close()
    connection.close()

    return uid

def update_sql_by_uid(uid):

    try:
        uid = int(uid)
    except:
        return None

    ## user_mapping中暂定至多存1k万用户        
    if uid > 10000000:
        return None

    uname = collect_one_user_name(uid)

    connection, cursor = connect_sql()
    if type(uname) != type(None):
        query = "INSERT INTO user_mapping (uid, uname) VALUES (%s, %s) AS new ON DUPLICATE KEY UPDATE uname = new.uname"
        cursor.execute(query, (uid, uname))
        connection.commit()
    cursor.close()
    connection.close()

    return uname
