import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from validators import url

from page_analyzer.bs import get_status_code, get_values
from page_analyzer.db import Database

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    db = Database(DATABASE_URL)
    urls = db.get_urls()
    db.close_conn()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    url_ = str(request.form.to_dict()['url'])
    name = urlparse(url_).scheme + '://' + urlparse(url_).netloc
    correct_url = url(url_)
    if not correct_url:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422
    db = Database(DATABASE_URL)
    existing = db.get_url_by_name(name)
    if existing:
        flash('Страница уже существует', 'warning')
    else:
        db.add_url(name)
        flash('Страница успешно добавлена', 'success')
    url_id = db.get_url_id(name)
    db.close_conn()
    return redirect(url_for('show_url', id=url_id))


@app.get('/urls/<id>')
def show_url(id):
    db = Database(DATABASE_URL)
    url = db.get_url(id)
    url_checks = db.get_url_checks(id)
    db.close_conn()
    return render_template('url.html', url=url,
                           url_checks=url_checks)


@app.post('/urls/<id>/checks')
def urls_checks(id):
    db = Database(DATABASE_URL)
    url = db.get_url(id).name
    try:
        status_code = get_status_code(url)
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))
    h1, title, description = get_values(url)
    db.add_url_checks(id, status_code, h1, title, description)
    if status_code != 200:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        flash('Страница успешно проверена', 'success')
    db.close_conn()
    return redirect(url_for('show_url', id=id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_has_problem(e):
    return render_template('500.html'), 500
