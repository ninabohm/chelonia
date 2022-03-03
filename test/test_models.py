import unittest
from model.models import Booking
from model.models import User


class TestBooking(unittest.TestCase):

    def test_should_return_booking_venue_name(self):
        sample_booking = Booking("Jan", "Baeder11", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.venue_name, "Baeder11")

    def test_generate_datetime_selector(self):
        sample_booking = Booking("Jan", "Baeder11", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.generate_datetime_selector(), ".event-time[data-time='2022-03-04T19:00:00+00:00']")

    def test_should_return_first_name(self):
        sample_user = User("Jan", "Roschke")
        self.assertEqual(sample_user.first_name, "Jan")

    def test_return_user_name(self):
        mock_user = User("Jan", "Tiger")
        sample_booking = Booking(mock_user, "Bad13", "2022-03-04T19:00:00+00:00")
        self.assertEqual(sample_booking.user.last_name, "Tiger")
