from psycopg2.extras import RealDictCursor
from datetime import date
import psycopg2


class DataBase():
    def __init__(self, DATABASE_URL):
        self.conn = psycopg2.connect(DATABASE_URL)

    def select(self, query, values=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result

    def insert(self, query, values=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self.conn.commit()

    def get_site(self, id):
        select_query = 'SELECT * FROM urls WHERE id = %s;'
        site = self.select(select_query, (id,))[0]
        return site

    def get_sites(self):
        select_query = '''SELECT
                          urls.id AS id, urls.name AS name,
                          url_checks.status_code AS status_code,
                          MAX(url_checks.created_at) AS created_at
                          FROM urls
                          LEFT JOIN url_checks
                          ON urls.id = url_checks.url_id
                          GROUP BY urls.id, url_checks.status_code
                          ORDER BY id DESC;'''
        sites = self.select(select_query)
        return sites

    def get_name_urls(self):
        select_query = 'SELECT name FROM urls;'
        names = self.select(select_query)
        return names

    def get_url_name(self, id):
        select_query = 'SELECT name FROM urls WHERE id = %s;'
        site = self.select(select_query, (id,))[0]['name']
        return site

    def get_url_id(self, sort_url):
        select_query = 'SELECT id FROM urls WHERE name = %s;'
        id = self.select(select_query, (sort_url,))[0]['id']
        return id

    def get_checks(self, id):
        select_query = '''SELECT id, status_code, h1, title,
                          description, created_at
                          FROM url_checks
                          WHERE url_id = %s
                          ORDER BY id DESC;'''
        checks = self.select(select_query, (id,))
        return checks

    def add_url(self, sort_url):
        insert_query = '''INSERT INTO urls (name, created_at)
                          VALUES (%s, %s);'''
        created_at = date.today()
        self.insert(insert_query, (sort_url, created_at))

    def add_checks(self, id, status_code, h1, title, description):
        insert_query = '''INSERT INTO url_checks
                          (url_id, status_code, h1,
                          title, description, created_at)
                          VALUES (%s, %s, %s, %s, %s, %s);'''
        created_at = date.today()
        self.insert(insert_query,
                    (id, status_code, h1, title, description, created_at))

    def close_conn(self):
        self.conn.close()
