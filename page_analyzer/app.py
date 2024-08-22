from flask import Flask, url_for, render_template
from flask import flash, get_flashed_messages, request, redirect
from dotenv import load_dotenv
from validators import url
from urllib.parse import urlparse
from datetime import date
from bs4 import BeautifulSoup
from page_analyzer.db import DataBase
import os
import requests


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def sites():
    conn = DataBase(DATABASE_URL)
    select_query = '''SELECT
                      urls.id AS id, urls.name AS name,
                      url_checks.status_code AS status_code,
                      MAX(url_checks.created_at) AS created_at
                      FROM urls
                      LEFT JOIN url_checks
                      ON urls.id = url_checks.url_id
                      GROUP BY urls.id, url_checks.status_code
                      ORDER BY id DESC;'''
    sites = conn.select(select_query)
    return render_template('sites.html', sites=sites)


@app.post('/urls')
def urls_post():
    url_ = str(request.form.to_dict()['url'])
    sort_url = urlparse(url_).scheme + '://' + urlparse(url_).netloc
    correct_url = url(url_)
    if not correct_url:
        flash('Некорректный URL', 'error')
        return render_template('index.html'), 422
    conn = DataBase(DATABASE_URL)
    select_query = 'SELECT name FROM urls;'
    names = (tumple['name'] for tumple in conn.select(select_query))
    if sort_url in names:
        flash('Страница уже существует', 'warning')
    else:
        insert_query = '''INSERT INTO urls (name, created_at)
                          VALUES (%s, %s);'''
        created_at = date.today()
        conn.insert(insert_query, (sort_url, created_at))
        flash('Страница успешно добавлена', 'success')
    select_query = 'SELECT id FROM urls WHERE name = %s;'
    id = conn.select(select_query, (sort_url,))[0]['id']
    return redirect(url_for('url_id', id=id))


@app.get('/urls/<id>')
def url_id(id):
    conn = DataBase(DATABASE_URL)
    select_query = 'SELECT * FROM urls WHERE id = %s;'
    site = conn.select(select_query, (id,))[0]
    select_query = '''SELECT id, status_code, h1, title,
                      description, created_at
                      FROM url_checks
                      WHERE url_id = %s
                      ORDER BY id DESC;'''
    checks = conn.select(select_query, (id,))
    return render_template('url.html', site=site,
                           checks=checks)


@app.post('/urls/<id>/checks')
def urls_checks(id):
    conn = DataBase(DATABASE_URL)
    created_at = date.today()
    select_query = 'SELECT name FROM urls WHERE id = %s;'
    site = conn.select(select_query, (id,))[0]['name']
    try:
        status_code = requests.get(site).status_code
    except Exception:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_id', id=id))
    select_query = '''INSERT INTO url_checks
                      (url_id, status_code, h1,
                      title, description, created_at)
                      VALUES (%s, %s, %s, %s, %s, %s);'''
    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'lxml')
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.find('title').text if soup.find('title') else ''
    description = ''
    metas = soup.find_all('meta')
    for i in metas:
        if i.get('name', '') == 'description':
            description = i['content']
            break
    conn.insert(select_query,
                (id, status_code, h1, title, description, created_at))
    if status_code != 200:
       flash('Произошла ошибка при проверке', 'error')
    else:
       flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_id', id=id))
