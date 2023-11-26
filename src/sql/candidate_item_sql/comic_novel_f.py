from src.sql.connect import connect_sql
import pandas as pd

conn, cursor = connect_sql(dict=1)

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `rank`>0 \
        AND `type` = 1 \
        AND total > 50 \
        AND `score`> 6   "



cursor.execute(query)
res = cursor.fetchall()
df = pd.DataFrame(res)
df = df[df.platform.isin(['小说', '漫画'])]
df = df[df.nsfw==0]
df = df[df["tags"].apply(lambda x: "童年" not in x )]

df1 = df[df.platform.isin(['小说'])]
df1[["sid", "name", "name_cn"]].to_csv("data/filting_data/novel.csv", index=False)

df2 = df[df.platform.isin(['漫画'])]
df2[["sid", "name", "name_cn"]].to_csv("data/filting_data/comic.csv", index=False)
