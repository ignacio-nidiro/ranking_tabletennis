import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cur.execute(query, params or ())
        self.conn.commit()

    def fetch_all(self, query, params=None):
        self.cur.execute(query, params or ())
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()