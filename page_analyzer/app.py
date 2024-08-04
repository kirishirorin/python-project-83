from flask import Flask, url_for, render_template, flash, get_flashed_messages, request, redirect
from dotenv import load_dotenv
from validators import url
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import os
import psycopg2
import datetime



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
    with conn.cursor() as cursor:
        select_query = 'SELECT id, name FROM urls ORDER BY created_at DESC;'
        cursor.execute(select_query)
        sites = [{'id': id, 'name': name} for id, name in cursor.fetchall()]
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
            now_time = datetime.datetime.now()
            cursor.execute(insert_query, (sort_url, now_time))
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
    with conn.cursor() as cursor:
        select_query = 'SELECT * FROM urls WHERE id = %s;'
        cursor.execute(select_query, (id))
        result = cursor.fetchone()
        site = {'id': result[0], 'name': result[1], 'created_at': result[2]}
    conn.close()
    return render_template('url.html', site=site, messages=messages)