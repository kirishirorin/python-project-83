from flask import Flask, url_for, render_template
from flask import flash, request, redirect
from dotenv import load_dotenv
from validators import url
from urllib.parse import urlparse
from page_analyzer.db import DataBase
from page_analyzer.bs import get_status_code, get_values
import os


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    db = DataBase(DATABASE_URL)
    urls = db.get_sites()
    db.close_conn()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    url_ = str(request.form.to_dict()['url'])
    name = urlparse(url_).scheme + '://' + urlparse(url_).netloc
    correct_url = url(url_)
    if not correct_url:
        flash('Некорректный URL', 'error')
        return render_template('index.html'), 422
    db = DataBase(DATABASE_URL)
    names = (tumple.name for tumple in db.get_name_urls())
    if name in names:
        flash('Страница уже существует', 'warning')
    else:
        db.add_url(name)
        flash('Страница успешно добавлена', 'success')
    url_id = db.get_url_id(name)
    db.close_conn()
    return redirect(url_for('show_url', id=url_id))


@app.get('/urls/<id>')
def show_url(id):
    db = DataBase(DATABASE_URL)
    url = db.get_site(id)
    url_checks = db.get_checks(id)
    db.close_conn()
    return render_template('url.html', url=url,
                           url_checks=url_checks)


@app.post('/urls/<id>/checks')
def urls_checks(id):
    db = DataBase(DATABASE_URL)
    url = db.get_url_name(id)
    try:
        status_code = get_status_code(url)
    except Exception:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('show_url', id=id))
    h1, title, description = get_values(url)
    db.add_checks(id, status_code, h1, title, description)
    if status_code != 200:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
    db.close_conn()
    return redirect(url_for('show_url', id=id))
