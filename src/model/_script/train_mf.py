from src.sql.connect import connect_sql
import numpy as np
import pandas as pd

from src.model.embedding.embedding_f import MF
from src.model.embedding.vecsql_f import create_mf_vec_sql

conn,cursor = connect_sql(dict=1)

query = f"SELECT DISTINCT(uid) FROM `collectForTrain`"
cursor.execute(query)
res = pd.DataFrame(cursor.fetchall())
uid_list = list(res["uid"])


query = f"SELECT DISTINCT(sid) FROM `collectForTrain`"
cursor.execute(query)
res = pd.DataFrame(cursor.fetchall())
sid_list = list(res["sid"])



model = MF(uid_list, sid_list, d= 32, lr = 0.1)
model.train(n_epochs = 5)
# create_mf_vec_sql()
# model.save_model2sql()
model.save_model()