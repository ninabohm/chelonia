import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from flask import Flask
from flask import render_template, request, redirect
from dotenv import load_dotenv
from flask_login import LoginManager
from model.models import db
from model.models import Booking
from model.models import User
from forms.forms import RegistrationForm, LoginForm

load_dotenv()


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.logger.setLevel(logging.INFO)

# does this need to go?
db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
def index():
    return "hello jan"


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        return redirect('/')
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        user = User()
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        password = request.form.get('password')
        user.password_hash = user.set_password(password)
        db.session.add(user)
        db.session.commit()
        app.logger.info(f"added user {user.first_name} {user.last_name} with id {user.id} to db")
        return redirect('/login')
    return render_template("register.html", form=form)


@app.route('/booking')
def start_booking():
    driver = webdriver.Chrome('./chromedriver')
    new_booking = Booking(user, "74", "2022-03-04T19:00:00+00:00")
    db.session.add(new_booking)
    db.session.commit()
    app.logger.info(f"added new booking with booking_id {new_booking.id}")
    url = "https://pretix.eu/Baeder/74/"
    datetime_selector = new_booking.generate_datetime_selector()
    driver.get(url)
    booking_date = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    booking_date.click()

    # apply_voucher(driver)
    # complete_checkout(driver)
    return render_template("booking.html")


def apply_voucher(driver):
    voucher_field = driver.find_element(By.ID, "voucher")
    voucher_field.click()
    voucher_field.send_keys("urbansportsclub")

    voucher_submit_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-block btn-primary']")
    voucher_submit_button.click()

    add_to_cart_button = driver.find_element(By.ID, "btn-add-to-cart")
    add_to_cart_button.click()
    time.sleep(3)


def complete_checkout(driver):
    try:
        checkout_url = "https://pretix.eu/Baeder/74/checkout/customer/"
        driver.get(checkout_url)

        login_radio = driver.find_element(By.ID, "input_customer_login")
        login_radio.click()
        time.sleep(3)

        website_login(driver)

        confirmation_checkbox = driver.find_element(By.ID, "input_confirm_confirm_text_0")
        confirmation_checkbox.click()
        confirmation_checkbox.send_keys(Keys.TAB)
        confirmation_checkbox.send_keys(Keys.ENTER)

    except NoSuchElementException as error:
        print(error)


def website_login(driver):
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
    port = int(os.environ.get('PORT'))
    app.run(debug=True, host='0.0.0.0', port=port)

