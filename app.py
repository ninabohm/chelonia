import time
import logging
import os
from os import environ
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, g, render_template, request, redirect, flash, url_for, jsonify, session
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from model.models import db, Booking, User, Venue, Reservation
from forms.forms import RegistrationForm, LoginForm, VenueForm, BookingForm
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['APP_SETTING'] = environ.get('APP_SETTINGS')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
app.logger.setLevel(logging.INFO)

db.init_app(app)

with app.app_context():
    migrate = Migrate(app, db)
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
    form.venue_id.choices = venue_choices
    if request.method == 'POST':
        venue_id = request.form.get("venue_id")
        date_event = request.form.get("date_event")
        time_event = request.form.get("time_event")
        booking = Booking(venue_id, date_event, time_event, current_user.id)
        db.session.add(booking)
        db.session.commit()
        app.logger.info(f"added booking at venue {booking.venue_id} with id {booking.id}")
        reservation(booking.id)
        return redirect(url_for('get_bookings'))
    return render_template("create_booking.html", form=form)


@app.route('/reservation/<string:booking_id>', methods=['GET', 'POST'])
@requires_logged_in
def reservation(booking_id):
    if request.method == 'POST':
        reservation = Reservation(booking_id, current_user.id)
        db.session.add(reservation)
        db.session.commit()
        start_reservation(booking_id, reservation.id)

    reservations = []
    for item in db.session.query(Reservation).all():
        reservations.append(item)
    return render_template("reservations.html", reservations=reservations)


def start_reservation(booking_id, reservation_id):
    # driver = webdriver.Chrome('./chromedriver')
    booking_venue = db.session.query(Venue).join(Booking).filter_by(id=booking_id).first()
    venue_url = booking_venue.venue_url
    datetime_selector = generate_datetime_selector(booking_id)


def generate_datetime_selector(booking_id):
    date_event = db.session.query(Booking.date_event).filter_by(id=booking_id).first()[0]
    time_event = db.session.query(Booking.time_event).filter_by(id=booking_id).first()[0]
    time_event_formatted = datetime.strptime(time_event, '%H:%M')
    time_event_corrected = time_event_formatted - timedelta(hours=+1)
    # this is still wrong!
    datetime_selector = f".event-time[data-time='{date_event}T{time_event_corrected}:00+00:00']"

    # datetime_selector = ".event-time[data-time='2022-03-04T19:00:00+00:00']"
    print(datetime_selector)
    return datetime_selector


def backup_start_reservation():
    driver = webdriver.Chrome('./chromedriver')
    venue_url = "https://pretix.eu/Baeder/74/"
    # datetime_selector =
    driver.get(venue_url)
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

