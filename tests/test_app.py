import unittest
from unittest import mock
from views import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from model.models import *
from flask import url_for, request
from flask_login import current_user


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        db.session.close()
        db.drop_all()
        self.client = app.test_client
        db.create_all()
        self.booking = {}

    def test_given_app_running_index_endpoint_returns_200(self):
        response = self.client().get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

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

    def test_should_return_false_given_more_than_96_ahead(self):
        date_event = "2022-03-16"
        time_event = "20:00"
        new_booking = Booking("4", date_event, time_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_reservation_possible_now(booking.id, current_datetime))

    def test_should_return_false_given_more_than_96_ahead_2(self):
        date_event = "2023-04-26"
        time_event = "20:00"
        new_booking = Booking("4", date_event, time_event, "1")
        new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_reservation_possible_now(booking.id, current_datetime))


    def test_should_return_true_given_less_than_96_ahead_2(self):
        date_event = "2022-03-10"
        time_event = "20:00"
        new_booking = Booking("4", date_event, time_event, "2")
        new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
        db.session.commit()
        booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
        current_datetime = datetime(2022, 3, 10, 14, 2, 13, 440752)
        self.assertTrue(check_if_reservation_possible_now(booking.id, current_datetime))

    def test_given_booking_should_return_reservation_time(self):
        date_event = "2022-03-15"
        time_event = "20:00"
        booking = Booking("4", date_event, time_event, "1")
        expected = datetime(2022, 3, 11, 20, 0)
        earliest_time = calculate_earliest_reservation_datetime(booking)
        self.assertEqual(earliest_time, expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_reservation_datetime = datetime(2022, 3, 11, 10, 0)
        expected = 86400
        self.assertEqual(calculate_timedelta_in_seconds(earliest_reservation_datetime, current_datetime), expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds_2(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_reservation_datetime = datetime(2022, 3, 10, 10, 2)
        expected = 120
        self.assertEqual(calculate_timedelta_in_seconds(earliest_reservation_datetime, current_datetime), expected)

    # def test_should_return_reservation(self):
    #     date_event = "2022-03-15"
    #     time_event = "13:00"
    #     new_booking = Booking("4", date_event, time_event, "1")
    #     db.session.add(new_booking)
    #     db.session.commit()
    #     new_booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(new_booking)
    #     db.session.commit()
    #     booking = db.session.query(Booking).order_by(Booking.id.desc()).first()
    #     current_datetime_str = "2022-03-10 13:00:00.000000"
    #     actual = create_reservation_schedule_task(booking.id, current_datetime_str)
    #     self.assertIsInstance(actual, Reservation)

    def test_given_no_login_get_booking_returns_401(self):
        response = self.client().get("/booking", follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_given_no_login_get_user_returns_401(self):
        response = self.client().get("/user", follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_given_no_login_get_venue_returns_401(self):
        response = self.client().get("/venue", follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_post_user_login(self):
        response = self.client().post('/user/login')
        self.assertEqual(response.status_code, 200)

    @mock.patch('flask_login.utils._get_user')
    def test_given_login_get_booking_returns_200(self, current_user):
        data = {
            'email': 'alice@wonderland.com',
            'password': 'supersecure'
        }
        current_user.return_value = mock.Mock(is_authenticated=True, **data)
        response = self.client().get("/booking", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @mock.patch('flask_login.utils._get_user')
    def test_given_login_get_venue_returns_200(self, current_user):
        data = {
            'email': 'alice@wonderland.com',
            'password': 'supersecure'
        }
        current_user.return_value = mock.Mock(is_authenticated=True, **data)
        response = self.client().get("/venue", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_should_return_venue_url(self):
        venue = Venue("somename", "https://pretix.eu/Baeder/74/")
        db.session.add(venue)
        db.session.commit()
        db.session.query(Venue)
        venue_db = db.session.query(Venue).order_by(Venue.id.desc()).first()
        booking = Booking(venue_db.id, "2022-03-11", "20:00", "1")
        db.session.add(booking)
        db.session.commit()
        booking_db = db.session.query(Booking).order_by(Booking.id.desc()).first()
        venue_url = db.session.query(Venue.venue_url).join(Booking).filter_by(id=booking_db.id).first()[0]
        self.assertEqual(venue_url, 'https://pretix.eu/Baeder/74/')
