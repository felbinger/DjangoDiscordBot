#!/bin/bash

# shellcheck disable=SC2164
cd ./app/

# migrate database models
python3 manage.py migrate

# create admin user
python3 manage.py createsuperuser --username=user --email=

# load fixtures (settings database model entries)
python3 manage.py loaddata settings.yaml

# run server with asgi (starts the bot)
gunicorn app.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level DEBUG
