from psycopg2.extras import NamedTupleCursor, RealDictCursor
from datetime import date
import psycopg2


class DataBase():
    def __init__(self, DATABASE_URL):
        self.conn = psycopg2.connect(DATABASE_URL)

    def select(self, query, values=None, cursor=NamedTupleCursor):
        with self.conn.cursor(cursor_factory=cursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return result

    def insert(self, query, values=None):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self.conn.commit()

    def get_site(self, url_id):
        select_query = 'SELECT * FROM urls WHERE id = %s;'
        url = self.select(select_query, (url_id,))[0]
        return url

    def get_sites(self):
        select_query_urls = '''SELECT id, name
                               FROM urls
                               ORDER BY id DESC;'''
        select_query_url_checks = '''SELECT url_id, status_code, MAX(created_at)
                                     FROM url_checks
                                     GROUP BY url_id, status_code;'''
        urls = self.select(select_query_urls, cursor=RealDictCursor)
        url_checks = self.select(select_query_url_checks, cursor=RealDictCursor)
        total_urls = []
        for url in urls:
            i = 0
            for check in url_checks:
                if url['id'] == check.get('url_id', ''):
                    url_copy = url
                    check_copy = check
                    check_copy.pop('url_id')
                    url_copy.update(check_copy)
                    total_urls.append(url_copy)
                    i = 1
                    break
            if i == 0:
                total_urls.append(url)
        return total_urls

    def get_name_urls(self):
        select_query = 'SELECT name FROM urls;'
        names = self.select(select_query)
        return names

    def get_url_name(self, url_id):
        select_query = 'SELECT name FROM urls WHERE id = %s;'
        url = self.select(select_query, (url_id,))[0].name
        return url

    def get_url_id(self, name):
        select_query = 'SELECT id FROM urls WHERE name = %s;'
        url_id = self.select(select_query, (name,))[0].id
        return url_id

    def get_checks(self, url_check_id):
        select_query = '''SELECT id, status_code, h1, title,
                          description, created_at
                          FROM url_checks
                          WHERE url_id = %s
                          ORDER BY id DESC;'''
        checks = self.select(select_query, (url_check_id,))
        return checks

    def add_url(self, name):
        insert_query = '''INSERT INTO urls (name, created_at)
                          VALUES (%s, %s);'''
        created_at = date.today()
        self.insert(insert_query, (name, created_at))

    def add_checks(self, url_id, status_code, h1, title, description):
        insert_query = '''INSERT INTO url_checks
                          (url_id, status_code, h1,
                          title, description, created_at)
                          VALUES (%s, %s, %s, %s, %s, %s);'''
        created_at = date.today()
        self.insert(insert_query,
                    (url_id, status_code, h1, title, description, created_at))

    def close_conn(self):
        self.conn.close()
