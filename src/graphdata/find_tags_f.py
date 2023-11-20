import pandas as pd
from src.sql.connect import connect_sql
from sqlalchemy import create_engine

class MixGraphDBFindTag:

    def find_subjects_by_tag(self, tag_name):

        query = f"""
                MATCH (s:Subject)-[r:HAS_TAG]->(t:Tag)
                WHERE r.count >= 10 AND t.name = '{tag_name}'
                RETURN s.id;
                """

        result = self.exec_read(query)
        return [record["s.id"] for record in result]

    def find_subjects_by_ORtags(self, tag_names):
        query = """
            MATCH (s:Subject)-[r:HAS_TAG]->(t:Tag)
            WHERE r.count >= 10 AND t.name IN $tag_names
            RETURN s.id;
            """
        result = self.exec_read(query, {'tag_names': tag_names})
        return [record["s.id"] for record in result]

    def find_subjects_by_ANDtags(self, tag_names):
        N = len(tag_names)
        assert N >= 2
        s = self.find_subjects_by_tag(tag_names[0])
        if len(s) == 0:
            return []
        else:
            s = set(s)

        for i in range(1,N):
            t = tag_names[i]
            s &= set(self.find_subjects_by_tag(t))

            if len(s) == 0:
                return []
        
        return list(s)


    def find_subjects_by_tags(self, tags):
        if type(tags) == str:
            return self.find_subjects_by_tag(tags)
        
        elif type(tags) == list:
            if type(tags[0]) == type([]):
                s = set([])
                for ts in tags:
                    if len(ts) == 1:
                        s |= set(self.find_subjects_by_tag(ts[0])) 
                    else:
                        s |= set(self.find_subjects_by_ANDtags(ts))
                return list(s)

            else:
                if len(tags) == 1:
                    return self.find_subjects_by_tag(tags[0])
                else:
                    return self.find_subjects_by_ANDtags(tags)
            
        else:
            return None
