import sys
import pyspark
from pyspark.ml.recommendation import ALS, ALSModel
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField
from pyspark.sql.types import StringType, FloatType, IntegerType, LongType
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from recommenders.utils.timer import Timer

from recommenders.evaluation.spark_evaluation import SparkRatingEvaluation, SparkRankingEvaluation
from recommenders.utils.spark_utils import start_or_get_spark

from src.model.F.rec import get_read_item_id, check_sid_list
from src.sql.query_f import query_item_info_by_sidlist
from src.sql.connect import connect_sql

import numpy as np
import pandas as pd


spark = start_or_get_spark("ALS PySpark", memory="1g")
spark.conf.set("spark.sql.analyzer.failAmbiguousSelfJoin", "false")

class MsALS:
    def __init__(self, fp) -> None:
        
        self.model = ALSModel.load(fp)

    def rankitem(self, uid, **args):
        """
        TODO: 
            候选集还要改，内存不太够用，大概要吃1个G,而且有泄露的风险
        """
        topk = args.get("topk", 10)
        
        read_item_id = get_read_item_id(uid)
        candidate_sid_list = args["candidate_sid"]
        
        candidate_sid_list = list( set(candidate_sid_list) - read_item_id)

        user_subset = spark.createDataFrame([(uid,)], ["uid"])
        user_subset_recs = self.model.recommendForUserSubset(user_subset, 100)
        first_row = user_subset_recs.first()

        res = pd.DataFrame(first_row["recommendations"],columns=["sid","score"])

        res_sid_list  = check_sid_list(list(res.sid), set(read_item_id), uid, topk)
        res_df = pd.DataFrame(query_item_info_by_sidlist(sid_list = res_sid_list))

        if len(res_df) == 0:
            return None

        res = res.set_index("sid")
        topk_score = res.loc[list(res_df.sid)].score
        
        res_df["trans_score"] = list(topk_score)
        # res_df = res_df[res_df["trans_score"] > 0]

        return res_df.sort_values(by="trans_score", ascending=False)


    