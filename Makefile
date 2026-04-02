PORT ?= 8000

install:
	poetry install

dev: create_meta
	poetry run flask --debug --app page_analyzer:app run

start: create_meta
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start: create_meta
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest

create_meta:
	python -m page_analyzer.scripts.create_meta

reset_meta:
	python -m page_analyzer.scripts.reset_meta
