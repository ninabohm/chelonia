import unittest
from app import app, generate_datetime_selector, start_reservation, get_confirmation_code, check_if_less_than_96_hours_ahead
from model.models import Reservation
from flask_login import current_user
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class TestApp(unittest.TestCase):

    def test_given_app_running_index_endpoint_returns_200(self):
        with app.test_client() as client:
            response = client.get("/")
            assert response._status_code == 200

    def test_returns_correct_datetime_selector(self):
        with app.app_context():
            booking_id = "26"
            self.assertEqual(generate_datetime_selector(booking_id), ".event-time[data-time='2022-03-07T19:15:00+00:00']")

    # def test_starts_selenium_with_url(self):
    #     with app.app_context():
    #         booking_id = "26"
    #         user_id = "2"
    #         new_reservation = start_reservation(booking_id, user_id)
    #         self.assertIsInstance(new_reservation, Reservation)

    def test_returns_confirmation_code_from_url(self):
        with app.app_context():
            url = "https://pretix.eu/Baeder/74/order/WMHPW/pddi5nhiweavfy3r/?thanks=1"
            ser = Service('./chromedriver')
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(service=ser, options=options)
            driver.get(url)

            self.assertEqual(get_confirmation_code(driver), "WMHPW")

    def test_should_return_true_given_less_than_96_ahead(self):
        with app.app_context():
            booking_id = "36"
            self.assertTrue(check_if_less_than_96_hours_ahead(booking_id))

    def test_should_return_false_given_more_than_96_ahead(self):
        with app.app_context():
            booking_id = "38"
            self.assertFalse(check_if_less_than_96_hours_ahead(booking_id))

    def test_should_return_false_given_more_than_96_ahead_2(self):
        with app.app_context():
            booking_id = "39"
            self.assertFalse(check_if_less_than_96_hours_ahead(booking_id))

