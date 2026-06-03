PORT ?= 8000

install:
	poetry install

create_meta:
	alembic check || \
	alembic revision --autogenerate -m 'alembic upgrade' && alembic upgrade head

reset_meta:
	alembic downgrade base
	rm alembic/versions/*.py

db-start:
	docker compose -f db-compose.yaml up -d

db-stop:
	docker compose -f db-compose.yaml up -d

dev: db-start create_meta
	poetry run flask --debug --app page_analyzer:app run --port 8080

prod: db-start create_meta
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest
