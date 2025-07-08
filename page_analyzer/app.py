from flask import Flask, render_template, \
     request, redirect, url_for, flash, get_flashed_messages, abort
import os
from urllib.parse import urlparse
from validators.url import url as validate
from datetime import date
from .repositories import UrlsRepository, ChecksRepository
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

urls_repo = UrlsRepository()
checks_repo = ChecksRepository()


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
        return redirect(url_for('url_show', _id=same_url_data['id']))

    # Подготавливаем данные и заносим в базу
    url_data = prepare_url_data(trans_url)
    urls_repo.save(url_data)
    flash('Страница успешно добавлена', 'alert alert-success')
    return redirect(url_for('url_show', _id=url_data['id']))


@app.route('/urls/<int:_id>')
def url_show(_id):
    url_data = urls_repo.find_by_id(_id)
    checks_data = checks_repo.find(_id)
    if not url_data:
        abort(404)

    message = get_flashed_messages(with_categories=True)
    return render_template('url_show.html', url_data=url_data,
                           checks_data=checks_data, message=message)


@app.post('/urls/<int:_id>/checks')
def checks_post(_id):
    url_data = urls_repo.find_by_id(_id)
    if not url_data:
        abort(404)

    resp = send_request(url_data['name'])
    if not resp:
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('url_show', _id=_id))

    check_data = prepare_check_data({
        'url_id': _id,
        'resp': resp
    })
    checks_repo.save(check_data)
    flash('Страница успешно проверена', 'alert alert-success')
    return redirect(url_for('url_show', _id=_id))


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


def parse_resp(resp):
    soup = BeautifulSoup(resp.text, 'html.parser')
    try:
        title = soup.head.title.get_text()
    except AttributeError:
        title = ''
    try:
        description = soup.find(
            'meta', attrs={'name': 'description'}).get('content')
    except AttributeError:
        description = ''
    try:
        h1_content = ', '.join(el.get_text(strip=True)
                               for el in soup.body.find_all('h1'))
    except AttributeError:
        h1_content = ''

    return dict(title=title, description=str(description),
                h1_content=h1_content)


def prepare_url_data(data):
    return {'name': data, 'created_at': date.today()}


def prepare_check_data(data):
    tags = {}
    status_code = data['resp'].status_code
    if status_code == 200:
        tags = parse_resp(data['resp'])
    return dict(
        url_id=data['url_id'],
        created_at=date.today(),
        status_code=status_code,
        **tags
        )


def send_request(url):
    try:
        resp = requests.get(url, allow_redirects=True, timeout=3.0)
        resp.raise_for_status()
        return resp
    except HTTPError:
        if 400 <= resp.status_code < 500:
            return resp
    except Exception:
        return None
