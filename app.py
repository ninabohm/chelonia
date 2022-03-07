import time
import logging
import os
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from model.models import db, Booking, User, Venue
from forms.forms import RegistrationForm, LoginForm, VenueForm, BookingForm

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
    return User.query.get(user_id)


def requires_logged_in(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if '_user_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapped_func


def requires_not_logged_in(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if '_user_id' in session:
            return redirect(url_for('create_booking'))
        return func(*args, **kwargs)
    return wrapped_func


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/user/register', methods=['GET', 'POST'])
@requires_not_logged_in
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        user = User()
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.password = request.form.get('password')
        try:
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"added user {user.first_name} {user.last_name} with id {user.id} to db")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            return render_template("register.html", form=form, error=IntegrityError)
    return render_template("register.html", form=form)


@app.route('/user')
@requires_logged_in
def get_users():
    users = []
    for user in db.session.query(User).all():
        users.append(user)
    return render_template('users.html', users=users)


@app.route('/user/login', methods=['GET', 'POST'])
@requires_not_logged_in
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template("login.html", form=form)


@app.route('/user/logout')
@requires_logged_in
def logout():
    app.logger.info(f"ending session {session}")
    logout_user()
    return redirect(url_for('login'))


@app.route('/venue')
@requires_logged_in
def get_venues():
    app.logger.info(f"GET venues called by user {current_user.id}")
    venues = []
    for venue in db.session.query(Venue).all():
        venues.append(venue)
    return render_template("venues.html", venues=venues)


@app.route('/venue/create', methods=['GET', 'POST'])
@requires_logged_in
def create_venue():
    form = VenueForm()
    if request.method == 'POST':
        venue_name = request.form.get("venue_name")
        venue_url = request.form.get("venue_url")
        venue = Venue(venue_name, venue_url)
        db.session.add(venue)
        db.session.commit()
        app.logger.info(f"added venue {venue.venue_name} with id {venue.id}")
        return redirect(url_for('get_venues'))
    return render_template("create_venue.html", form=form)


@app.route('/booking')
@requires_logged_in
def get_bookings():
    bookings = []
    for booking in db.session.query(Booking).all():
        bookings.append(booking)
    return render_template("bookings.html", bookings=bookings)


@app.route('/booking/create', methods=['GET', 'POST'])
@requires_logged_in
def create_booking():
    available_venues = db.session.query(Venue).all()
    venue_choices = [(item.id, item.venue_name) for item in available_venues]
    form = BookingForm()
    form.venue_name.choices = venue_choices
    app.logger.info(f"venue choices: {venue_choices}")
    if request.method == 'POST':
        venue_name = request.form.get("venue_name")
        date_event = request.form.get("date_event")
        time_event = request.form.get("time_event")
        venue_id = db.session.query(Venue.id).filter_by(venue_name=venue_name).first()
        # booking = Booking(venue_id[0], date_event, time_event, current_user.id)
        # db.session.add(booking)
        # db.session.commit()
        # app.logger.info(f"added booking at venue {booking.venue_id} with id {booking.id}")
        return redirect(url_for('get_bookings'))
    return render_template("create_booking.html", form=form)


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

