web: gunicorn -w 1 app:app --preload
worker: celery -A celery worker --loglevel INFO
