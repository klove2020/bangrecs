import pandas as pd
from src.sql.connect import connect_sql


class modelinit:
    def rankitem(self, uid, **_args):
        return pd.DataFrame([])

class HT:
    def __init__(self) -> None:
        self.item_sid_list = {}
        self._item_sid_list_init()

        self.field_name = list(self.item_sid_list.keys())

        self.model = {name:modelinit() for name in self.field_name}

        

    def _item_sid_list_init(self):

        def _read_fun(p):
            return list(pd.read_csv(p)["sid"])
        
        self.item_sid_list["anime"] = _read_fun("data/filting_data/anime.csv")
        self.item_sid_list["anime_nsfw"] = _read_fun("data/filting_data/anime_nsfw.csv")
        
        self.item_sid_list["comic"] = _read_fun("data/filting_data/comic.csv")
        self.item_sid_list["comic_nsfw"] = _read_fun("data/filting_data/comic_nsfw.csv")
        self.item_sid_list["novel"] = _read_fun("data/filting_data/novel.csv")
        
        self.item_sid_list["galgame"] = _read_fun("data/filting_data/galgame.csv")
        self.item_sid_list["tv"] = _read_fun("data/filting_data/tv.csv")
        
    def rankitem(self, uid, **args):
        t = args["type"]
        topk = args["topk"]
        
        if t == 4:
            return self.model["galgame"].rankitem(uid, **args)
        if t == 6:
            return self.model["tv"].rankitem(uid, **args)

        type_counts = self._counts_type(uid, t, topk)

        def ff(_field):
            _num = [type_counts[f] for f in _field]
            _num_dict = {f:num for f,num in zip(_field, _num)}
            
            s = 0
            for f in _field:
                s += type_counts[f]
            
            _prob_dict = {f:num/s for f,num in _num_dict.items()}
            _return_num_dict = {f: int(p * topk) for f,p in _prob_dict.items()}

            res = []
            for f in _field:
                num = _return_num_dict[f]
                if num == 0:
                    res.append(pd.DataFrame([]))
                else:
                    _args = args
                    _args["topk"] = num
                    res.append(self.model[f].rankitem(uid, **_args)) 
            return pd.concat(res)

        if t == 2:
            _field = ["anime", "anime_nsfw"]
            return ff(_field)
        
        if t == 1:
            _field = ["comic", "comic_nsfw", "novel"]
            return ff(_field)  
        
        if t == 0:
            _field = self.field_name
            return ff(_field)
            
    def _counts_type(self, uid, t, topk):
        conn, cursor = connect_sql(dict=1)
        
        if t == 0:
            query = f"SELECT sid FROM collect WHERE uid = {uid} ORDER BY timestamp DESC LIMIT 0, {topk}"
        else:
            query = f"SELECT sid FROM collect WHERE uid = {uid} AND subject_type = {t} ORDER BY timestamp DESC LIMIT 0, {topk}"
        
        cursor.execute(query)
        res = cursor.fetchall()
        recent_id_list = list(pd.DataFrame(res).sid)

        if len(recent_id_list) == 0:
            print("没有观看记录")
            return None

        # 初始化一个字典来记录每种类型的数量
        type_counts = {type_name: 0 for type_name in self.item_sid_list.keys()}

        # 遍历recent_id_list中的每个sid
        for sid in recent_id_list:
            # 检查sid属于哪种类型
            for type_name, sid_list in self.item_sid_list.items():
                if sid in sid_list:
                    type_counts[type_name] += 1
                    break

        return type_counts


