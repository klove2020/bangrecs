from src.sql.connect import connect_sql


conn, cursor = connect_sql(dict=1)

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `rank`>0 \
        AND `type` = 2 \
        AND total>1000 \
        AND nsfw=0"

import pandas as pd

cursor.execute(query)
res = cursor.fetchall()

df=pd.DataFrame(res)

df[df["platform"] == "剧场版"]
df[df["platform"] == "TV"]