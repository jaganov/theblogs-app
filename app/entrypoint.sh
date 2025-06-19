#!/bin/sh
echo "--- STARTED APP --- "
# Cron
# service cron restart
# python manage.py crontab add
# python manage.py crontab show
#python manage.py crontab remove
#python manage.py collectstatic
#python manage.py runserver 0.0.0.0:8000
python manage.py collectstatic --no-input --clear
gunicorn app.wsgi --access-logfile - --workers 4 --max-requests 5000 --max-requests-jitter 100 --preload
#gunicorn app.asgi:application -b 0.0.0.0:8000 -k app.uvicorn_worker.UvicornWorker
echo "--- END APP --- "
exec "$@"