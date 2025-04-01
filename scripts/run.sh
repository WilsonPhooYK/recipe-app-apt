#!/bin/sh

# Anything fail will fail the whole script
set -e

python manage.py wait_for_db
# Collect all static files and put them in the STATIC_ROOT directory
python manage.py collectstatic --noinput
# Run all migrations automatically whenever the container starts
python manage.py migrate

# --workers: Set 4 diff workers for uwsgi
# --master: Enable the master process
# --enable-threads: Enable threads
# --module: The WSGI module to use (Entry point)
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi