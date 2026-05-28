# Page Analyzer

[![Hexlet Check](https://github.com/EgorTitov01/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/EgorTitov01/python-project-83/actions)
[![Test, coverage, lint](https://github.com/EgorTitov01/python-project-83/actions/workflows/tests_linter_ci.yml/badge.svg)](https://github.com/EgorTitov01/python-project-83/actions/workflows/tests_linter_ci.yml)

Page Analyzer — веб-приложение для базовой SEO-проверки сайтов.

Сервис позволяет добавить URL, выполнить проверку доступности страницы и получить основные SEO-данные: HTTP-код ответа, заголовок `h1`, содержимое тега `title` и мета-описание `description`.

## Демо

Веб-сервис доступен по ссылке:

https://python-project-83-a50c.onrender.com/

## Возможности

- добавление сайта по URL;
- валидация введённого адреса;
- нормализация URL до схемы и домена;
- защита от повторного добавления одного и того же сайта;
- запуск проверки страницы;
- получение HTTP-кода ответа;
- парсинг SEO-данных страницы:
  - `h1`;
  - `title`;
  - `description`;
- сохранение истории проверок;
- отображение списка добавленных сайтов и результатов проверок.

## Стек технологий

- Python 3.10+
- Flask
- PostgreSQL
- SQLAlchemy
- Alembic
- Requests
- BeautifulSoup4
- Gunicorn
- Poetry
- Docker Compose

## Установка

Склонируйте репозиторий:

```bash
git clone https://github.com/EgorTitov01/python-project-83.git
cd python-project-83
````

Установите зависимости:

```bash
make install
```

## Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp your.env .env
```

Заполните переменные окружения:

```env
SECRET_KEY=your-secret-key

POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
PG_HOST=localhost
PG_PORT=5432
POSTGRES_DB=page_analyzer

DB_AUTH="${POSTGRES_USER}:${POSTGRES_PASSWORD}@${PG_HOST}:${PG_PORT}/${POSTGRES_DB}"
DATABASE_URL="postgresql+psycopg://${DB_AUTH}"
```

## Запуск базы данных

Для локального запуска PostgreSQL через Docker Compose,
создания и применения миграций и запуска можно воспользоваться
командами:

```bash
make dev
```
для запуска в режиме разработки, или
```bash
make prod
```
для запуска production-сервера gunicorn


После запуска приложение будет доступно по адресу:

```text
http://localhost:(PORT)
```

По умолчанию PORT=8080 для dev-сервера, для prod PORT=8000.


## Проверка качества кода

Запуск линтера:

```bash
make lint
```

Запуск тестов:

```bash
make test
```

## Основные команды

| Команда            | Описание                               |
| ------------------ | -------------------------------------- |
| `make install`     | Установка зависимостей через Poetry    |
| `make db-start`    | Запуск PostgreSQL через Docker Compose |
| `make create_meta` | Создание и применение миграций Alembic |
| `make dev`         | Запуск приложения в режиме разработки  |
| `make prod`        | Запуск приложения через Gunicorn       |
| `make lint`        | Проверка кода линтером Flake8          |
| `make test`        | Запуск тестов                          |

## Структура проекта

```text
.
├── page_analyzer/
│   ├── app.py              # Flask-приложение и маршруты
│   ├── models.py           # SQLAlchemy-модели таблиц
│   ├── repositories.py     # Работа с базой данных
│   └── scripts/
├── templates/              # HTML-шаблоны
├── alembic/                # Миграции базы данных
├── database.sql            # SQL-структура таблиц (deprecated)
├── db-compose.yaml         # Docker Compose для PostgreSQL
├── pyproject.toml          # Зависимости и настройки проекта
├── Makefile                # Команды для разработки
└── README.md
```

## Как пользоваться

1. Откройте главную страницу приложения.
2. Введите URL сайта, например:

```text
https://example.com
```

3. Нажмите кнопку проверки.
4. Если URL корректный, сайт будет добавлен в базу данных.
5. На странице сайта нажмите «Запустить проверку».
6. Приложение сохранит результат проверки и покажет:

   * код ответа сервера;
   * заголовок `h1`;
   * содержимое `title`;
   * мета-описание `description`;
   * дату проверки.

## Автор

Egor Titov
