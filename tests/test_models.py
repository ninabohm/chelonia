import unittest
from model.models import *
from views import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


class TestBooking(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        db.session.close()
        db.drop_all()
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
        date_event = "2022-03-10"
        time_event = "14:00"
        new_booking = Booking(venue_id, date_event, time_event, user.id)
        db.session.add(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        self.assertEqual(booking.user_id, user.id)

    def test_given_reservation_return_booking_id(self):
        with app.app_context():
            with app.test_client() as client:
                client.get('/')
                new_user = User()
                db.session.add(new_user)
                db.session.commit()
                user = db.session.query(User).order_by(User.id.desc()).first()
                current_user = user
                venue_id = "12"
                date_event = "2022-03-10"
                time_event = "14:00"
                new_booking = Booking(venue_id, date_event, time_event, user.id)
                db.session.add(new_booking)
                db.session.commit()
                booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
                reservation = Reservation(booking.id)
                db.session.add(reservation)
                db.session.commit()
                self.assertEqual(reservation.booking_id, booking.id)
