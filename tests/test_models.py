import unittest
from model.models import *
from views import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


class TestBooking(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        print(app.config)
        db.session.close()
        db.drop_all()
        self.client = app.test_client
        db.create_all()

    def test_should_return_first_name(self):
        sample_user = User()
        sample_user.first_name = "Jan"
        self.assertEqual(sample_user.first_name, "Jan")

    def test_should_return_true_given_hash_is_correct(self):
        password = "blabla"
        hashed = generate_password_hash(password)
        self.assertTrue(check_password_hash(hashed, password))

    def test_should_return_true_given_hash_matches(self):
        user = User()
        password = "bliblablubb"
        user.password_hash = generate_password_hash(password)
        self.assertTrue(check_password_hash(user.password_hash, password))

    def test_user_check_pw_should_return_true_given_hash_matches(self):
        user = User()
        password = "bliblablubb"
        user.password_hash = generate_password_hash(password)
        self.assertTrue(user.check_password(password))

    def test_user_check_pw_should_return_true_given_correct_pw_set(self):
        user = User()
        user.password = "blaaaa"
        self.assertTrue(user.check_password("blaaaa"))

    def test_given_new_booking_should_return_user_id(self):
        new_user = User()
        db.session.add(new_user)
        db.session.commit()
        user = db.session.query(User).order_by(User.id.desc()).first()
        venue_id = "12"
        datetime_event = datetime(2022, 3, 10, 14, 0)
        new_booking = Booking(venue_id, datetime_event, user.id)
        db.session.add(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        self.assertEqual(booking.user_id, user.id)

    def test_given_ticket_return_booking_id(self):
        with app.app_context():
            with app.test_client() as client:
                client.get('/')
                new_user = User()
                db.session.add(new_user)
                db.session.commit()
                user = db.session.query(User).order_by(User.id.desc()).first()
                current_user = user
                venue_id = "12"
                datetime_event = datetime(2022, 3, 10, 14, 0)
                new_booking = Booking(venue_id, datetime_event, user.id)
                db.session.add(new_booking)
                db.session.commit()
                booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
                ticket = Ticket(booking.id, current_user.id)
                db.session.add(ticket)
                db.session.commit()
                self.assertEqual(ticket.booking_id, booking.id)

