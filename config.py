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
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    CELERY_RESULT_BACKEND = os.environ['CELERY_RESULT_BACKEND']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
