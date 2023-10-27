from src.sql.connect import connect_sql
from src.datacls.user_f import User, ActiveUserList
import json

class MixUiAttri:
    """
    记录非初始化之外的属性和相关的维护
    """

    def get_item_info(self, sid):

        connection,cursor = connect_sql()

        # SQL query
        query = "SELECT * FROM item_info WHERE sid = %s"
        cursor.execute(query, (sid,))                
        result = cursor.fetchone()

        # Close the cursor and the connection
        cursor.close()
        connection.close()
        
        if result:
            json_fields = ['tags', 'infobox', 'collection', "count", 'images']  # Add any other fields that are stored as JSON
            for field in json_fields:
                if result.get(field):
                    result[field] = json.loads(result[field])

        return result


    def fetch_user_map(self):
        connection, cursor = connect_sql()

        # 查询所有记录
        cursor.execute('SELECT uid, uname FROM user_mapping')
        records = cursor.fetchall()

        cursor.close()
        connection.close()
        data = records

        # 构建两个字典
        self.uid_to_uname = {record[0]: record[1] for record in data}
        self.uname_to_uid = {record[1]: record[0] for record in data}

    def add_user(self, uid):
        u = User()
        u.uid = uid
        self.user_dict[uid] = u

    def get_user(self, uid):
        if uid not in self.user_dict.keys():
            self.add_user(uid)
        return self.user_dict[uid]
