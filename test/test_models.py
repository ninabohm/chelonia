import unittest
from model.models import Booking
from model.models import User
from werkzeug.security import generate_password_hash, check_password_hash


class TestBooking(unittest.TestCase):

    def test_should_return_booking_venue_name(self):
        sample_booking = Booking("Jan", "Baeder11", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.venue_name, "Baeder11")

    def test_generate_datetime_selector(self):
        sample_booking = Booking("Jan", "Baeder11", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.generate_datetime_selector(), ".event-time[data-time='2022-03-04T19:00:00+00:00']")

    def test_should_return_first_name(self):
        sample_user = User()
        sample_user.first_name = "Jan"
        self.assertEqual(sample_user.first_name, "Jan")

    def test_return_user_name(self):
        mock_user = User()
        mock_user.first_name = "Jan"
        mock_user.last_name = "Tiger"
        sample_booking = Booking(mock_user, "Bad13", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.user.last_name, "Tiger")

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
        print(user.password_hash)
        self.assertTrue(user.check_password("blaaaa"))
