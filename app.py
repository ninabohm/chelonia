import logging
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_celery import make_celery
from flask_session import Session


app = Flask(__name__)
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")
app.logger.setLevel(logging.INFO)
sess = Session()

celery = make_celery(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

sess.init_app(app)

import views
