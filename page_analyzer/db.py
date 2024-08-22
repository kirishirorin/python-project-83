from psycopg2.extras import RealDictCursor
import psycopg2


class DataBase():
    def __init__(self, DATABASE_URL):
        self.DATABASE_URL = DATABASE_URL

    def select(self, query, values=None):
        conn = psycopg2.connect(self.DATABASE_URL)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        conn.close()
        return result

    def insert(self, query, values=None):
        conn = psycopg2.connect(self.DATABASE_URL)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            conn.commit()
        conn.close()
