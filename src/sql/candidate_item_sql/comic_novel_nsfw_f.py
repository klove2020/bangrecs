from src.sql.connect import connect_sql
import pandas as pd

conn, cursor = connect_sql(dict=1)


"""
    注意: 交互数据量非常少
"""

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `type` = 1 \
        AND total > 10 \
        AND `score`> 5 \
        AND `nsfw` = 1 "



cursor.execute(query)
res = cursor.fetchall()
df = pd.DataFrame(res)
df = df[df.platform.isin(['小说', '漫画'])]


df[["sid", "name", "name_cn"]].to_csv("data/filting_data/comic_nsfw.csv", index=False)
