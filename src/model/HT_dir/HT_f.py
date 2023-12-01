import pandas as pd
from src.sql.connect import connect_sql
from sqlalchemy import create_engine

class modelinit:
    def rankitem(self, uid, **_args):
        return pd.DataFrame([])

class HT:
    def __init__(self) -> None:
        self.item_sid_list = {}
        self._item_sid_list_init()        

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

        self.field_name = list(self.item_sid_list.keys())

        self.field2type_dict  = {
            "anime":2,
            "anime_nsfw":2,
            "comic":1,
            "comic_nsfw":1,
            "novel":1,
            "galgame":4,
            "tv":6
        }

        self.HT_item_list_table()
        
    def rankitem(self, uid, **args):
        t = args["type"]
        topk = args["topk"]
        print(f"{topk=}")
        
        if t == 4:
            _args = args.copy()
            _args["candidate_sid"] = list(set(args["candidate_sid"]) & set(self.item_sid_list["galgame"]) )
            _args["type"] = 4
            return self.model["galgame"].rankitem(uid, **_args)
        
        if t == 6:
            _args = args.copy()
            _args["candidate_sid"] = list(set(args["candidate_sid"]) & set(self.item_sid_list["tv"]) )
            _args["type"] = 6
            return self.model["tv"].rankitem(uid, **_args)

        type_counts = self._counts_type(uid, t, topk)
        print("\n\n")
        print(f"{type_counts=}")

        def ff(_field):
            _num = [type_counts[f] for f in _field]
            _num_dict = {f:num for f,num in zip(_field, _num)}
            
            s = 0
            for f in _field:
                s += type_counts[f]
            
            _prob_dict = {f:num/s for f,num in _num_dict.items()}
            _return_num_dict = {f: int(p * topk) for f,p in _prob_dict.items()}

            print(f"{_return_num_dict=}")

            
            res = []

            def _fun_res(res, _return_num_dict, _field):
                new_return_num_dict = {}
                for f in _field:
                    num = _return_num_dict[f]
                    print(f"{f},{num}")

                    if num == 0:
                        new_return_num_dict[f] = 0
                        res.append(pd.DataFrame([]))
                    else:                    
                        _args = args.copy()
                        _args["topk"] = num
                        _args["candidate_sid"] = list(set(args["candidate_sid"]) & set(self.item_sid_list[f]) )   
                        _args["type"] = self.field2type_dict[f]                 

                        _df = self.model[f].rankitem(uid, **_args)
                        if type(_df) == type(None):
                            actual_num = 0
                        else:
                            actual_num = len(_df)
                        
                        new_return_num_dict[f] = actual_num

                        # print(f"{new_return_num_dict=}")
                        res.append(_df)
                        # print(_df) 

                shortfall_field = []
                full_field = []
                short_total_num = 0
                for f in _field:
                    nn = _return_num_dict[f] - new_return_num_dict[f]  
                    short_total_num += nn
                    if nn == 0:
                        full_field.append(f)
                    else:
                        shortfall_field.append(f)

                return res, short_total_num, full_field, shortfall_field
            
            res, short_total_num, full_field, shortfall_field = _fun_res(res, _return_num_dict, _field)
            
            max_iter = 4
            ii = 0
            while short_total_num > 0:
                ii += 1
                if ii >= max_iter:
                    break

                tdf = pd.concat(res)
                if len(tdf)>0:
                    args["candidate_sid"] =  list(set(args["candidate_sid"]) - set(tdf.sid))                    
                else:
                    full_field = [i for i in self.field_name if i not in shortfall_field]

                if len(full_field) == 0:
                    break

                # print(f"{short_total_num=}, {len(full_field)=}")
                
                full_field = full_field[:short_total_num]
                field_num_list = split_integer(short_total_num, len(full_field))
                _return_num_dict_2 = {f:n for f,n in zip(full_field, field_num_list)}
                print(f"random split dict, {_return_num_dict_2}")

                res, short_total_num, full_field, shortfall_field = _fun_res(res, _return_num_dict_2, full_field)



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
            query = f"""
            SELECT c.sid FROM collect c
            JOIN HT_item_list t ON c.sid = t.sid
            WHERE c.uid = {uid} 
            ORDER BY c.timestamp DESC 
            LIMIT 0, {topk}
            """
        else:
            query = f"""
            SELECT c.sid FROM collect c
            JOIN HT_item_list t ON c.sid = t.sid
            WHERE c.uid = {uid} 
            AND t.subject_type = {t} 
            ORDER BY c.timestamp DESC 
            LIMIT 0, {topk}
            """
        
        cursor.execute(query)
        res = cursor.fetchall()
        recent_id_list = list(pd.DataFrame(res).sid)

        if len(recent_id_list) == 0:
            print("没有观看记录")
            return None

        # 初始化一个字典来记录每种类型的数量
        type_counts = {type_name: 0 for type_name in self.item_sid_list.keys()}

        for sid in recent_id_list:
            for type_name, sid_list in self.item_sid_list.items():
                if sid in sid_list:
                    type_counts[type_name] += 1
                    break

        return type_counts


    def HT_item_list_table(self):

        data_to_append = []
        for f in self.field_name:
            sid_list = self.item_sid_list[f]
            st = self.field2type_dict[f]
            c = f
            
            for sid in sid_list:
                data_to_append.append({"sid": sid, "subject_type": st, "class": c})            

        df = pd.DataFrame(data_to_append)
        engine = create_engine("mysql+pymysql://root:abc159753@localhost/bangumi")

        # 将DataFrame写入新的SQL表
        df.to_sql('HT_item_list', con=engine, index=False, if_exists='replace')



import random
def split_integer(num, parts):    
    if parts > num:
        assert False
    indices = sorted(random.sample(range(1, num), parts - 1))
    return [j - i for i, j in zip([0] + indices, indices + [num])]
