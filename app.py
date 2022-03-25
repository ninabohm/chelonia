import logging
import os

import json_log_formatter
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_celery import make_celery
from flask_session import Session

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.FileHandler(filename='/var/log/chelonia-log.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger('chelonia-log')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")
app.config['TIMEZONE'] = "UTC"
sess = Session()

celery = make_celery(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

sess.init_app(app)




import views
