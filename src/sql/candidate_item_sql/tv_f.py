from src.sql.connect import connect_sql


conn, cursor = connect_sql(dict=1)

# `date`>='2005-1-1' \
query = "SELECT * FROM item_info WHERE  \
        `rank`>0 \
        AND `type` = 6 \
        AND total > 100 \
        AND `score`> 6  "


import pandas as pd

cursor.execute(query)
res = cursor.fetchall()

df = pd.DataFrame(res)

# df = df[df["tags"].apply(lambda x: "gal" in x )]

df[["sid", "name", "name_cn"]].to_csv("data/filting_data/tv.csv", index=False)

