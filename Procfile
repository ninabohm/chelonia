web: gunicorn -w 1 app:app --preload
worker: celery -A app.celery worker --loglevel INFO --concurrency 2
