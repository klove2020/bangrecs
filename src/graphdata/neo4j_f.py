from neo4j import GraphDatabase
import json
from .tags_f import MixGraphDBTag

class GraphDB(MixGraphDBTag):
    def __init__(self):
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "abc159753"
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()


    def exec_read(self, query, parameters=None):
        def _run(tx):
            result = tx.run(query, parameters)
            return [record for record in result]
        
        with self._driver.session() as session:
            return session.read_transaction(_run)

    def exec_write(self, query, parameters=None):
        def _run(tx, query, parameters):
            return tx.run(query, parameters)
        with self._driver.session() as session:
            return session.write_transaction(_run, query, parameters)


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

    def query_sid_hastags(self):
        query = """
            MATCH (s:Subject)
            WHERE s.effectiveTag IS NOT NULL
            RETURN s.id;
            """
        result = self.exec_read(query)
        return [record["s.id"] for record in result]

    def get_effectiveTag(self, sid):
        query = f"""
                MATCH (s:Subject)
                WHERE s.id = {sid}
                RETURN s.effectiveTag
                """
        result = self.exec_read(query)
        res = result[0]["s.effectiveTag"]
        if type(res) == type(None):
            return []
        else:
            return [i for i in res]



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

    def write_item_info_tags2neo4j(self, rows):
        with self._driver.session() as session:
            for row in rows:
                sid = row[0]
                tags = json.loads(row[1])
                for tag in tags:
                    tag_name = tag["name"]
                    tag_count = tag["count"]
                    session.execute_write(add_to_neo4j, sid, tag_name, tag_count)

def add_to_neo4j(tx, sid, tag_name, tag_count):
    tx.run("MERGE (s:Subject {id: $sid}) "
           "MERGE (t:Tag {name: $tag_name}) "
           "MERGE (s)-[:HAS_TAG {count: $tag_count}]->(t)",
           sid=sid, tag_name=tag_name, tag_count=tag_count)
