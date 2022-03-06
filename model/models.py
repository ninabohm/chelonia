from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String())
    password_hash = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # def __init__(self, first_name, last_name, email, password_hash):
    #     self.first_name = first_name
    #     self.last_name = last_name
    #     self.email = email
    #     self.password_hash = password_hash


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String())
    datetime_event = db.Column(db.String())

    def __init__(self, user, venue_name, datetime_event):
        self.user = user
        self.venue_name = venue_name
        self.datetime_event = datetime_event

    def generate_datetime_selector(self):
        return f".event-time[data-time='{self.datetime_event}']"


