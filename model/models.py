from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

db = SQLAlchemy(app)
with app.app_context():
    migrate = Migrate(app, db)
    db.create_all()
    app.logger.info("created all db tables")


class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    password_hash = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    authenticated = db.Column(db.Boolean, default=False)
    bookings = db.relationship("Booking", backref="user")
    tickets = db.relationship("Ticket", backref="user")
    venue_email = db.Column(db.String())
    venue_password = db.Column(db.String())
    birthday = db.Column(db.Date())
    street = db.Column(db.String())
    house_no = db.Column(db.String())
    postal_code = db.Column(db.String())
    city = db.Column(db.String())
    phone = db.Column(db.String())
    urban_sports_membership_no = db.Column(db.String())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class Booking(db.Model):

    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer(), db.ForeignKey("venue.id"))
    datetime_event = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    confirmation_code = db.Column(db.String())
    ticket = db.relationship("Ticket", backref="booking", uselist=False)
    earliest_ticket_datetime = db.Column(db.DateTime())

    def __init__(self, venue_id, datetime_event, user_id):
        self.venue_id = venue_id
        self.datetime_event = datetime_event
        self.user_id = user_id


class Ticket(db.Model):

    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer(), db.ForeignKey("booking.id"))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String())

    def __init__(self, booking_id, user_id):
        self.booking_id = booking_id
        self.status = "STARTED"
        self.user_id = user_id


class Venue(db.Model):

    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String())
    venue_url = db.Column(db.String())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    bookings = db.relationship("Booking", backref="venue")
    venue_type = db.Column(db.String())

    def __init__(self, venue_name, venue_url, venue_type):
        self.venue_name = venue_name
        self.venue_url = venue_url
        self.venue_type = venue_type


db.create_all()
app.logger.info("created all db tables - second")
