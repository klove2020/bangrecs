from src.sql.connect import connect_sql


conn, cursor = connect_sql(dict=1)

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `rank`>0 \
        AND `type` = 2 \
        AND total > 100 \
        AND nsfw=0 \
        AND `score`> 6   "


import pandas as pd

cursor.execute(query)
res = cursor.fetchall()

df = pd.DataFrame(res)

df = df[~df["tags"].apply(lambda x: "童年" in x or "欧美" in x )]
df = df[df.platform.isin(["TV", "OVA", "剧场版"])]

df[["sid", "name", "name_cn"]].to_csv("data/filting_data/anime.csv", index=False)

# df[df["platform"] == "剧场版"]
# df[df["platform"] == "TV"]
# df[df["platform"] == "OVA"]