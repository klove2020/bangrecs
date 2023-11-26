from src.sql.connect import connect_sql


conn, cursor = connect_sql(dict=1)

query = "SELECT * FROM item_info WHERE  \
        `date`>='2005-1-1' \
        AND `rank`>0 \
        AND `type` = 4 \
        AND total > 50 \
        AND `score`> 6   "


import pandas as pd

cursor.execute(query)
res = cursor.fetchall()

df = pd.DataFrame(res)

df = df[df["tags"].apply(lambda x: "gal" in x )]

df[["sid", "name", "name_cn"]].to_csv("data/filting_data/galgame.csv", index=False)

