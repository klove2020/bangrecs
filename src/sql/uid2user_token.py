# from src.sql.connect import connect_sql
import pandas as pd



import pandas as pd
from sqlalchemy import create_engine

import pandas as pd
import random
import string

# 生成 uid 列表（范围1到200万）
uid_list = list(range(1, 2000001))

# 生成 utoken 列表（随机字符串）
def generate_random_string(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

utoken_list = [generate_random_string() for _ in range(2000000)]

# 创建 DataFrame
df = pd.DataFrame({
    'uid': uid_list,
    'utoken': utoken_list
})

# 确保 uid 和 utoken 是一一对应的
assert df['uid'].is_unique
assert df['utoken'].is_unique

# 查看 DataFrame 的前几行
print(df.head())




def writ2sql(df):
    # 创建数据库连接
    engine = create_engine("mysql+pymysql://root:abc159753@localhost/bangumi")
    # 将DataFrame写入新的SQL表
    df.to_sql('uid2utoken', con=engine, index=False, if_exists='replace')


writ2sql(df)