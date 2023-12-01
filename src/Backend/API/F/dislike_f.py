from flask import jsonify, request
from src.sql.connect import connect_sql

import time

sql_name = "feedback_dislike"

def dislike_post():
    try:
        args_dict = request.json

        uid =int(args_dict["uid"]) 
        sid = int(args_dict["sid"])
        t = int(time.time())

        conn,cursor = connect_sql()

        # 构造 SQL 语句
        sql = f"""
        INSERT INTO {sql_name} (uid, sid, timestamp)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE timestamp = %s;
        """

        # 执行 SQL 语句
        cursor.execute(sql, (uid, sid, t, t))

        # 提交事务
        conn.commit()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Dislike registered."}), 200

    except Exception as e:            
            print("\n\b\n BBBBBug!:", str(e))
            return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500    

