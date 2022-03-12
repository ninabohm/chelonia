web: gunicorn app:app --preload
worker: celery -A celery worker --loglevel INFO
