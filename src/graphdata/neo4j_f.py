from neo4j import GraphDatabase
import json
from .tags_f import MixGraphDBTag
from .relation_f import MixGraphDBRelation
from .find_tags_f import MixGraphDBFindTag

class GraphDB(MixGraphDBTag, MixGraphDBRelation, MixGraphDBFindTag):
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
