import logging
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_celery import make_celery


app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/2'
app.logger.setLevel(logging.INFO)

celery = "make_celery(app)"

login_manager = LoginManager()
login_manager.init_app(app)

import views
