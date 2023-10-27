import mysql.connector

def connect_sql(dict = False):
    config = {
        'user': 'root',
        'password': 'abc159753',
        'host': 'localhost',
        'database': 'bangumi',
        'raise_on_warnings': True
    }

    connection = mysql.connector.connect(**config)
    if dict:
        cursor = connection.cursor(dictionary=True)
    else:
        cursor = connection.cursor()
    return connection, cursor
