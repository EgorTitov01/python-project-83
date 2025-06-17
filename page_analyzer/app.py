from flask import Flask, render_template, \
     request, redirect, url_for, flash, get_flashed_messages, abort
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
from validators.url import url as validate
from datetime import date
from .repositories import UrlsRepository, ChecksRepository


load_dotenv()
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
urls_repo = UrlsRepository(DATABASE_URL)
checks_repo = ChecksRepository(DATABASE_URL)


@app.route('/')
def index():
    message = []
    return render_template('index.html', message=message)


@app.route('/urls')
def urls_index():
    urls_data = urls_repo.get_content()
    return render_template('urls_index.html', urls_data=urls_data)


@app.post('/urls')
def urls_post():
    message = []
    url = request.form.get('url')
    # Проверяем введённый URL
    if not is_valid(url):
        message = [('alert alert-danger', "Некорректный URL")]
        return render_template('index.html', url=url, message=message), 422

    # Приводим URL к нужному виду и проверяем, нет ли его в базе данных
    trans_url = transform_url(url)
    same_url_data = urls_repo.find_by_url(trans_url)
    if same_url_data:
        flash('Страница уже существует', 'alert alert-info')
        return redirect(url_for('url_show', id=same_url_data['id']))

    # Подготавливаем данные и заносим в базу
    url_data = _format(url, 'url')
    urls_repo.save(url_data)
    flash('Страница успешно добавлена', 'alert alert-success')
    return redirect(url_for('url_show', id=url_data['id']))


@app.route('/urls/<int:id>')
def url_show(id):
    url_data = urls_repo.find_by_id(id)
    checks_data = checks_repo.find(id)
    if not url_data:
        abort(404)
    message = get_flashed_messages(with_categories=True)
    return render_template('url_show.html', url_data=url_data,
                           checks_data=checks_data, message=message)


@app.post('/urls/<int:id>/checks')
def checks_post(id):
    if not urls_repo.find_by_id(id):
        abort(404)
    check_data = {'url_id': id, 'created_at': date.today()}
    # Подготавливаем данные и заносим в базу
    check = _format(check_data, 'check')
    checks_repo.save(check)
    flash('Страница успешно проверена', 'alert alert-success')
    return redirect(url_for('url_show', id=id))


@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html'), 404


def transform_url(url):   # Убирает ненужные части URL
    parsed_url = urlparse(url)
    return parsed_url.scheme + '://' + parsed_url.netloc


def is_valid(url_str):
    return (
        validate(url_str, private=False, may_have_port=True)
        and len(url_str) <= 255
    )


def _format(data, category):
    if category == 'url':
        return {'name': data, 'created_at': date.today()}

    elif category == 'check':
        return {'url_id': data['url_id'], 'created_at': date.today()}
