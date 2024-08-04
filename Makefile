install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run --host=0.0.0.0

start_db:
	sudo service postgresql start

build:
	./build.sh

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
