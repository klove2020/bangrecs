import pandas as pd


# MATCH (subject1:Subject {id: 208559}), (subject2:Subject {id: 262996})
# RETURN EXISTS {
#     MATCH p=(subject1)-[:RELATION*..3]-(subject2)
#     WHERE all(r IN relationships(p) WHERE r.type IN [1, 1002, 1003, 1007, 1008, 4, 5, 6, 8, 1012, 4008, 12, 4006, 4012, 1005, 2, 4002, 1006, 3, 4003, 3001, 3003, 3004])
# } AS isConnected

class MixGraphDBRelation:
    def find_Is_relation(self, sid1, sid2):
        # query = """
        #     MATCH (subject1:Subject {id: $sid1}), (subject2:Subject {id: $sid2})
        #     RETURN EXISTS((subject1)-[:RELATION*..3]-(subject2)) AS isConnected
        #     """

        query = """
                MATCH (subject1:Subject {id: $sid1}), (subject2:Subject {id: $sid2})
                RETURN EXISTS {
                    MATCH p=(subject1)-[:RELATION*..3]-(subject2)
                    WHERE all(r IN relationships(p) WHERE r.type IN [1, 1002, 1003, 1007, 1008, 4, 5, 6, 8, 1012, 4008, 12, 4006, 4012, 1005, 2, 4002, 1006, 3, 4003, 3003, 3004])
                } AS isConnected
            """


        parameters={
                    'sid1': sid1,
                    'sid2': sid2,
                    }
        
        r = self.exec_read(query, parameters=parameters)
        return list(r[0])[0]

    def find_Is_relation_one_vs_list(self, sid, sid_lists):
        """
            sid_list: 2d list
        """
        N = len(sid_lists)
        for i in range(N):
            sid_list = sid_lists[i]
            
            ## 备选项最多4个
            if len(sid_list) > 4:
                continue

            sid_ = sid_list[0]
            is_rel = self.find_Is_relation(sid, sid_)
            
            if is_rel:
                sid_lists[i].append(sid)
                return True, sid_lists
        sid_lists.append([sid])
        return False, sid_lists

