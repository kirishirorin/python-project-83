from flask import Flask, url_for, render_template
from flask import flash, request, redirect
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
    sites = conn.get_sites()
    conn.close_conn()
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
    names = (tumple['name'] for tumple in conn.get_name_urls())
    if sort_url in names:
        flash('Страница уже существует', 'warning')
    else:
        conn.add_url(sort_url)
        flash('Страница успешно добавлена', 'success')
    id = conn.get_url_id(sort_url)
    conn.close_conn()
    return redirect(url_for('show_url', id=id))


@app.get('/urls/<id>')
def show_url(id):
    conn = DataBase(DATABASE_URL)
    site = conn.get_site(id)
    checks = conn.get_checks(id)
    conn.close_conn()
    return render_template('url.html', site=site,
                           checks=checks)


@app.post('/urls/<id>/checks')
def urls_checks(id):
    conn = DataBase(DATABASE_URL)
    created_at = date.today()
    site = conn.get_url_name(id)
    try:
        status_code = requests.get(site).status_code
    except Exception:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id))
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
    conn.add_checks(id, status_code, h1, title, description)
    if status_code != 200:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
    conn.close_conn()
    return redirect(url_for('show_url', id=id))
