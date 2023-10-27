import pandas as pd
from src.sql.connect import connect_sql
from sqlalchemy import create_engine

class MixGraphDBTag:
    def find_tags_with_more_than_some_subjects(self, num=10):
        query = f"""
            MATCH (s:Subject)-[r:HAS_TAG]->(t:Tag)
            WHERE r.count >= 10 WITH t,
            COUNT(DISTINCT s) AS subject_count
            WHERE subject_count >= {num}
            RETURN t.name, subject_count;
        """
        result = self.exec_read(query)
        return [(record["t.name"], record["subject_count"]) for record in result]

    def _update_sid_effectiveTag_by_tag(self, tag_name):
        query = f"""
            MATCH (t:Tag)<-[r:HAS_TAG]-(s:Subject)
            WHERE t.name = '{tag_name}' AND r.count >= 10 
            WITH s
            WHERE NOT '{tag_name}' IN coalesce(s.effectiveTag, [])
            SET s.effectiveTag = CASE 
                                WHEN s.effectiveTag IS NOT NULL THEN s.effectiveTag + ['{tag_name}']
                                ELSE ['{tag_name}']
                                END
            """
        self.exec_write(query)
        
    def _update_sid_effectiveTag(self):
        tags = self.find_tags_with_more_than_some_subjects()
        num = 0
        N = len(tags)
        for tag, count in tags:
            num += 1 
            self._update_sid_effectiveTag_by_tag(tag)
            print(f"{num=} / {N}, {tag=}")
    
    def get_effectiveTag_list(self):
        tags = self.find_tags_with_more_than_some_subjects()
        return [t[0] for t in tags]
    
    def tags_write2sql_cache(self):
        # conn, cursor = connect_sql()
        tlist = self.get_effectiveTag_list()

        table_name = "_cache_tags_list"
        df = pd.DataFrame(tlist,columns=["tag"])

        engine = create_engine("mysql+pymysql://root:abc159753@localhost/bangumi")
        # 将DataFrame写入新的SQL表
        df.to_sql(f'{table_name}', con=engine, index=False, if_exists='replace')

