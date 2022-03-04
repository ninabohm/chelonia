from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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


class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

