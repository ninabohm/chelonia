import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from model.models import Booking
from model.models import User
from flask import Flask
from flask import render_template
from dotenv import load_dotenv
from model.models import db
import os

load_dotenv()


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.logger.setLevel(logging.INFO)

db.init_app(app)

with app.app_context():
    db.create_all()


driver = webdriver.Chrome('./chromedriver')
user = User("Jan", "Roschke")


@app.route('/')
def index():
    return "Helloo :)"


@app.route('/booking')
def start_booking():
    new_booking = Booking(user, "74", "2022-03-04T19:00:00+00:00")
    db.session.add(new_booking)
    db.session.commit()
    app.logger.info(f"added new booking with booking_id {new_booking.id}")
    url = "https://pretix.eu/Baeder/74/"
    datetime_selector = new_booking.generate_datetime_selector()
    driver.get(url)
    booking_date = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    booking_date.click()

    # apply_voucher()
    # complete_checkout()
    return render_template("booking.html")


def apply_voucher():
    voucher_field = driver.find_element(By.ID, "voucher")
    voucher_field.click()
    voucher_field.send_keys("urbansportsclub")

    voucher_submit_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-block btn-primary']")
    voucher_submit_button.click()

    add_to_cart_button = driver.find_element(By.ID, "btn-add-to-cart")
    add_to_cart_button.click()
    time.sleep(3)


def complete_checkout():
    try:
        checkout_url = "https://pretix.eu/Baeder/74/checkout/customer/"
        driver.get(checkout_url)

        login_radio = driver.find_element(By.ID, "input_customer_login")
        login_radio.click()
        time.sleep(3)

        website_login()

        confirmation_checkbox = driver.find_element(By.ID, "input_confirm_confirm_text_0")
        confirmation_checkbox.click()
        confirmation_checkbox.send_keys(Keys.TAB)
        confirmation_checkbox.send_keys(Keys.ENTER)

    except NoSuchElementException as error:
        print(error)


def website_login():
    user_email = driver.find_element(By.ID, "id_login-email")
    user_email.send_keys("nina.boehm1994@gmail.com")
    user_password = driver.find_element(By.ID, "id_login-password")
    user_password.send_keys("Pgvx/pF4;87$")
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.ENTER)
    time.sleep(3)

    checkbox_save = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
    checkbox_save.click()
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.ENTER)
    time.sleep(3)


if __name__ == '__main__':
    app.run()
