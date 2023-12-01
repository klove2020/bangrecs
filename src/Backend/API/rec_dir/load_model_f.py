from src.sql.connect import connect_sql
from src.model.seqtransfer.seqtransfer_f import SeqTransfer
from src.model.embedding.rec_f import MFRec
from src.model.SARSRec_dir.SASRec4Bangumi_dir import SASRec4Bangumi
from src.model.BanTrans_dir.BanTrans_f import Bantrans4Bangumi
from src.model.HT_dir.HT_f import HT
from src.graphdata.neo4j_f import GraphDB
import pandas as pd


mfrec = MFRec(model_path="assets/MF/")


sarsrec = SASRec4Bangumi(
    model_path = "assets/sarsrec4bgm/SASRec.epoch=201.lr=0.001.layer=2.head=1.hidden=50.maxlen=200.pth",
    uid_mapping_path = "assets/sarsrec4bgm/uid_mapping.pkl",
    sid_mapping_path = "assets/sarsrec4bgm/sid_mapping.pkl"
)

bsrrec_gal = Bantrans4Bangumi(
    model_path = "assets/BanTrans/gal1/process_save/model_checkpoint3.pth",
    uid_mapping_path = "assets/BanTrans/gal1/process_save/uid_mapping.pkl",
    sid_mapping_path = "assets/BanTrans/gal1/process_save/sid_mapping.pkl"
)

bsrrec_anime_nsfw = Bantrans4Bangumi(
    model_path="assets/BanTrans/anime_nsfw_1/model10.pth",
    uid_mapping_path="assets/BanTrans/anime_nsfw_1/uid_mapping.pkl",
    sid_mapping_path="assets/BanTrans/anime_nsfw_1/sid_mapping.pkl"
)

## 模型没调好
# bsrrec_anime = Bantrans4Bangumi(
#     model_path="assets/BanTrans/anime_1/model_a2.pth",
#     uid_mapping_path="assets/BanTrans/anime_1/uid_mapping.pkl",
#     sid_mapping_path="assets/BanTrans/anime_1/sid_mapping.pkl"
# )

ht = HT()
ht.model["anime_nsfw"] = bsrrec_anime_nsfw
ht.model["galgame"] = bsrrec_gal

base_model = SeqTransfer("trans_ma")
ht.model["anime"] = base_model
ht.model["comic"] = base_model
ht.model["comic_nsfw"] = base_model
ht.model["novel"] = base_model
ht.model["tv"] = base_model
