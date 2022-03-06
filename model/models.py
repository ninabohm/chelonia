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
    email = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)

    bookings = db.relationship("Booking", backref="user")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Booking(db.Model):

    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer(), db.ForeignKey("venue.id"))
    date_event = db.Column(db.String())
    time_event = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, venue_id, date_event, time_event, user_id):
        self.venue_id = venue_id
        self.date_event = date_event
        self.time_event = time_event
        self.user_id = user_id

    def generate_datetime_selector(self):
        return f".event-time[data-time='{self.date_event} {self.time_event}']"


class Venue(db.Model):

    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String())
    venue_url = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    bookings = db.relationship("Booking", backref="venue")

    def __init__(self, venue_name, venue_url):
        self.venue_name = venue_name
        self.venue_url = venue_url

