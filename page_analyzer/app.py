from flask import Flask, url_for, render_template, flash, get_flashed_messages, request, redirect
from dotenv import load_dotenv
from validators import url
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from datetime import date
import os
import psycopg2



DATABASE_URL = os.getenv('DATABASE_URL')


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)

@app.get('/urls')
def sites():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        select_query = 'SELECT urls.id AS id, urls.name AS name, MAX(url_checks.created_at) AS created_at FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id GROUP BY urls.id;'
        cursor.execute(select_query)
        sites = cursor.fetchall()
    conn.close()
    return render_template('sites.html', sites=sites)

@app.post('/urls')
def urls_post():
    url_ = str(request.form.to_dict()['url'])
    sort_url = urlparse(url_).scheme + '//' + urlparse(url_).netloc
    correct_url = url(url_)
    if not correct_url:
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'))
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        select_query = 'SELECT name FROM urls;'
        cursor.execute(select_query)
        names = (tumple[0] for tumple in cursor.fetchall())
        if sort_url in names:
            flash('Страница уже существует', 'warning')
        else:
            insert_query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s);'
            created_at = date.today()
            cursor.execute(insert_query, (sort_url, created_at))
            conn.commit()
            flash('Страница успешно добавлена', 'success')
        select_query = 'SELECT id FROM urls WHERE name = %s;'
        cursor.execute(select_query, (sort_url,))
        id = cursor.fetchone()[0]
    conn.close()
    return redirect(url_for('url_id', id=id))

@app.get('/urls/<id>')
def url_id(id):
    messages = get_flashed_messages(with_categories=True)
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        select_query = 'SELECT * FROM urls WHERE id = %s;'
        cursor.execute(select_query, (id,))
        site = cursor.fetchone()
        select_query = 'SELECT id, status_code, h1, title, description, created_at FROM url_checks WHERE url_id = %s ORDER BY created_at DESC;'
        cursor.execute(select_query, (id,))
        checks = cursor.fetchall()
    conn.close()
    return render_template('url.html', site=site, messages=messages, checks=checks)

@app.post('/urls/<id>/checks')
def urls_checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        select_query = 'INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, %s);'
        created_at = date.today()
        status_code = 0
        h1 = ''
        title = ''
        description = ''
        cursor.execute(select_query, (id, status_code, h1, title, description, created_at))
        conn.commit()
        flash('Страница успешно проверена', 'success')
    conn.close()
    return redirect(url_for('url_id', id=id))
