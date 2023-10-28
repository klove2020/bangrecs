from SARSRec_dir.SASRec4Bangumi_dir import SASRec4Bangumi

mp = "bangumi_default/SASRec.epoch=201.lr=0.001.layer=2.head=1.hidden=50.maxlen=200.pth"
uid_mapping_path, sid_mapping_path = "save/uid_mapping.pkl", "save/sid_mapping.pkl"
model = SASRec4Bangumi(mp, uid_mapping_path, sid_mapping_path)


res = model.rankitem_sids([126173, 126461, 261805])

print(1 + 1)