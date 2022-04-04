import unittest, pytz
from unittest import mock
from views import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from model.models import *
from forms.forms import *


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config.from_object("config.TestingConfig")
        db.session.close()
        db.drop_all()
        self.client = app.test_client
        db.create_all()

    def test_given_app_running_index_endpoint_returns_200(self):
        response = self.client().get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_returns_correct_datetime_selector(self):
        datetime_event_utc = datetime(2022, 3, 7, 19, 15)
        new_booking = Booking("4", datetime_event_utc, "1")
        db.session.add(new_booking)
        db.session.commit()
        self.assertEqual(generate_datetime_selector(new_booking.id), ".event-time[data-time='2022-03-07T19:15:00+00:00']")

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
        datetime_event = datetime(2022, 3, 16, 20, 0)
        new_booking = Booking("4", datetime_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.commit()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_ticket_possible_now(new_booking.id, current_datetime))

    def test_should_return_false_given_more_than_96_ahead_2(self):
        datetime_event = datetime(2022, 4, 26, 20, 0)
        new_booking = Booking("4", datetime_event, "1")
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.commit()
        current_datetime = datetime(2022, 3, 10, 8, 27, 7, 637999)
        self.assertFalse(check_if_ticket_possible_now(new_booking.id, current_datetime))


    def test_should_return_true_given_less_than_96_ahead_2(self):
        datetime_event = datetime(2022, 3, 10, 20, 0)
        new_booking = Booking("4", datetime_event, "2")
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.commit()
        current_datetime = datetime(2022, 3, 10, 14, 2, 13, 440752)
        self.assertTrue(check_if_ticket_possible_now(new_booking.id, current_datetime))

    def test_given_booking_should_return_ticket_time(self):
        datetime_event = datetime(2022, 3, 15, 20, 0).astimezone(pytz.UTC)
        booking = Booking("4", datetime_event, "1")
        expected = datetime(2022, 3, 11, 20, 0).astimezone(pytz.UTC)
        self.assertEqual(calculate_earliest_ticket_datetime(booking), expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_ticket_datetime = datetime(2022, 3, 11, 10, 0)
        expected = 86400
        self.assertEqual(calculate_timedelta_in_seconds(earliest_ticket_datetime, current_datetime), expected)

    def test_given_earliest_time_should_return_timedelta_in_seconds_2(self):
        current_datetime = datetime(2022, 3, 10, 10, 0)
        earliest_ticket_datetime = datetime(2022, 3, 10, 10, 2)
        expected = 120
        self.assertEqual(calculate_timedelta_in_seconds(earliest_ticket_datetime, current_datetime), expected)

#     def test_given_no_login_get_booking_returns_401(self):
#         response = self.client().get("/booking", follow_redirects=True)
#         self.assertEqual(response.status_code, 401)

#     def test_given_no_login_get_user_returns_401(self):
#         response = self.client().get("/user", follow_redirects=True)
#         self.assertEqual(response.status_code, 401)
#
#     def test_given_no_login_get_venue_returns_401(self):
#         response = self.client().get("/venue", follow_redirects=True)
#         self.assertEqual(response.status_code, 401)

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
        venue = Venue("somename", "https://pretix.eu/Baeder/74/", "swimming")
        db.session.add(venue)
        db.session.commit()
        db.session.query(Venue)
        venue_db = db.session.query(Venue).order_by(Venue.id.desc()).first()
        booking = Booking(venue_db.id, datetime(2022, 3, 11, 20, 0), "1")
        db.session.add(booking)
        db.session.commit()
        venue_url = db.session.query(Venue.venue_url).join(Booking).filter_by(id=booking.id).first()[0]
        self.assertEqual(venue_url, 'https://pretix.eu/Baeder/74/')

    def test_should_return_booking_id(self):
        datetime_event = datetime(2022, 3, 16, 20, 0)
        new_booking = Booking("4", datetime_event, "1")
        db.session.add(new_booking)
        db.session.commit()
        new_booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(new_booking)
        db.session.commit()
        self.assertEqual(new_booking.id, 1)

    def test_should_return_ticket(self):
        booking = Booking("1", datetime(2022, 3, 12, 20, 0), "1")
        db.session.add(booking)
        db.session.commit()
        ticket = Ticket(booking.id, "3")
        db.session.add(ticket)
        db.session.commit()
        ticket_db = db.session.query(Ticket).join(Booking).filter_by(id=booking.id).first()
        self.assertEqual(ticket_db.id, ticket.id)

    @mock.patch('flask_login.utils._get_user')
    def test_given_correct_booking_details_returns_correct_datetime(self, current_user):
        data = {
            'email': 'alice@wonderland.com',
            'password': 'supersecure'
        }
        current_user.return_value.id = "3"
        venue_id = "1"
        date_event = "2022-04-01"
        time_event_cet = "07:00"

        booking = post_booking_and_save(venue_id, date_event, time_event_cet)
        booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(booking)
        db.session.add(booking)
        db.session.commit()

        expected = datetime(2022, 4, 1, 5, 0)
        actual = db.session.query(Booking).filter_by(id=booking.id).first().datetime_event
        self.assertEqual(expected, actual)

    # @mock.patch('flask_login.utils._get_user')
    # def test_given_venue_type_bouldering_returns_200(self, current_user):
    #     data = {
    #         'email': 'alice@wonderland.com',
    #         'password': 'password'
    #     }
    #
    #     current_user.return_value.id = "3"
    #     venue = Venue("basement", "blabla_url", "bouldering")
    #     db.session.add(venue)
    #     db.session.commit()
    #     booking = Booking("1", datetime(2022, 4, 2, 20, 0), "1")
    #     db.session.add(booking)
    #     db.session.commit()
    #
    #     response = self.client().post(f"/ticket/{booking.id}")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data, "bouldering ticket!!")

    def test_given_bouldering_ticket_returns_correct_datetimeselector(self):
        bouldering_venue = Venue("bla", "blubb", "bouldering")
        booking = Booking("1", datetime(2022, 4, 4, 20, 0), "1")
        db.session.add(bouldering_venue)
        db.session.add(booking)
        db.session.commit()
        self.assertEqual(generate_datetime_selector(booking.id), "//div[normalize-space()='4']")

    def test_given_bouldering_ticket_next_month_returns_correct_datetimeselector(self):
        bouldering_venue = Venue("bla", "blubb", "bouldering")
        booking = Booking("1", datetime(2022, 5, 1, 20, 0), "1")
        db.session.add(bouldering_venue)
        db.session.add(booking)
        db.session.commit()
        self.assertEqual(generate_datetime_selector(booking.id), "//div[normalize-space()='1']")

    def test_given_date_is_next_month_returns_true(self):
        booking = Booking("1", datetime(2022, 5, 1, 20, 0), "1")
        db.session.add(booking)
        db.session.commit()
        self.assertTrue(check_if_next_month(booking.id))

    def test_given_booking_returns_datetime(self):
        self.assertFalse(True)