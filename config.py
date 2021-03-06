import os
import redis


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS'))
    SESSION_TYPE = os.environ.get('SESSION_TYPE')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']


class TestingConfig(Config):
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
