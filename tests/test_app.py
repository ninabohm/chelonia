import unittest
from views import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from model.models import *


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        db.session.close()
        db.drop_all()
        db.create_all()

    def test_given_app_running_index_endpoint_returns_200(self):
        with app.test_client() as client:
            response = client.get("/")
            assert response._status_code == 200

    def test_returns_correct_datetime_selector(self):
        date_event = "2022-03-07"
        time_event = "20:15"
        new_booking = Booking("4", date_event, time_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        self.assertEqual(generate_datetime_selector(booking.id), ".event-time[data-time='2022-03-07T19:15:00+00:00']")

    def test_returns_confirmation_code_from_url(self):
        with app.app_context():
            url = "https://pretix.eu/Baeder/74/order/WMHPW/pddi5nhiweavfy3r/?thanks=1"
            ser = Service('./chromedriver')
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(service=ser, options=options)
            driver.get(url)

            self.assertEqual(get_confirmation_code(driver), "WMHPW")

    # disabled for testing purposes
    # def test_should_return_true_given_less_than_96_ahead(self):
    #     date_event = "2022-03-11"
    #     time_event = "10:00"
    #     new_booking = Booking("4", date_event, time_event, "1")
    #     db.session.add(new_booking)
    #     db.session.commit()
    #     booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
    #     current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
    #     self.assertTrue(check_if_less_than_96_hours_ahead(booking.id, current_datetime))

    def test_should_return_false_given_more_than_96_ahead(self):
        date_event = "2022-03-16"
        time_event = "20:00"
        new_booking = Booking("4", date_event, time_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_less_than_96_hours_ahead(booking.id, current_datetime))

    def test_should_return_false_given_more_than_96_ahead_2(self):
        date_event = "2023-04-26"
        time_event = "20:00"
        new_booking = Booking("4", date_event, time_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_less_than_96_hours_ahead(booking.id, current_datetime))

    def test_given_booking_should_return_reservation_time(self):
        date_event = "2022-03-15"
        time_event = "20:00"
        booking = Booking("4", date_event, time_event, "1")
        expected = datetime(2022, 3, 11, 20, 0)
        earliest_time = calculate_earliest_reservation_datetime(booking)
        self.assertEqual(earliest_time, expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_reservation_time = datetime(2022, 3, 11, 10, 0)
        expected = 86400
        self.assertEqual(calculate_timedelta_in_seconds(earliest_reservation_time, current_datetime), expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds_2(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_reservation_time = datetime(2022, 3, 10, 10, 2)
        expected = 120
        self.assertEqual(calculate_timedelta_in_seconds(earliest_reservation_time, current_datetime), expected)
