import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_celery import make_celery
from flask_session import Session


app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

logger = logging.getLogger()
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

app.config['TIMEZONE'] = "UTC"
sess = Session()

celery = make_celery(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

sess.init_app(app)

import views
