import os

broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/3')