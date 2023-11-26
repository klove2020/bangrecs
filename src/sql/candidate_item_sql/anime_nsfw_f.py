from src.sql.connect import connect_sql


conn, cursor = connect_sql(dict=1)

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `rank`>0 \
        AND `type` = 2 \
        AND total > 50 \
        AND nsfw=1 \
        AND `score`>= 5   "


import pandas as pd

cursor.execute(query)
res = cursor.fetchall()

df = pd.DataFrame(res)

df = df[df["tags"].apply(lambda x: "里番" in x )]

df[["sid", "name", "name_cn"]].to_csv("data/filting_data/anime_nsfw.csv", index=False)

