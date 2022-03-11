import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    DATADOG_ENV = os.environ['DATADOG_ENV']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    DATADOG_ENV = os.environ['DATADOG_ENV']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
