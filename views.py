from app import app, login_manager, celery
import time, json
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, g, render_template, request, redirect, flash, url_for, session, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from model.models import db, Booking, User, Venue, Reservation
from forms.forms import RegistrationForm, LoginForm, VenueForm, BookingForm
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
@login_required
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
@login_required
def logout():
    app.logger.info(f"ending session {session}")
    logout_user()
    return redirect(url_for('login'))


@app.route('/venue/create', methods=['GET', 'POST'])
@login_required
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


@app.route('/venue', methods=['GET'])
@login_required
def get_venues():
    venues = db.session.query(Venue).all()
    data = []
    for venue in venues:
        obj = {
            'id': venue.id,
            'venue_name': venue.venue_name,
            'venue_url': venue.venue_url,
            'created_at': venue.created_at,
            'bookings': venue.bookings
        }
        data.append(obj)
    response = app.response_class(
        response=json.dumps(data, default=str),
        status=200,
        mimetype='application/json'
    )
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        return response
    return render_template("venues.html", venues=data)


@app.route('/booking')
@login_required
def get_bookings():
    bookings = db.session.query(Booking).all()
    data = []
    for booking in bookings:
        data.append(booking)
    return render_template("bookings.html", bookings=bookings)


@app.route('/booking/create', methods=['GET', 'POST'])
@login_required
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
        booking.earliest_reservation_datetime = calculate_earliest_reservation_datetime(booking)
        db.session.commit()
        app.logger.info(f"added booking at venue {booking.venue_id} with id {booking.id}")
        create_reservation(booking.id)
        return render_template("booking_show.html", booking=booking)
    return render_template("create_booking.html", form=form)


@app.route('/reservation')
@login_required
def get_reservations():
    reservations = []
    for item in db.session.query(Reservation).all():
        reservations.append(item)
    return render_template("reservations.html", reservations=reservations)


@app.route('/reservation/<booking_id>', methods=['GET', 'POST'])
@login_required
def create_reservation(booking_id):
    if request.method == 'POST':
        current_datetime = datetime.utcnow()
        if check_if_reservation_possible_now(booking_id, current_datetime):
            return start_reservation(booking_id)
        current_datetime_str = str(current_datetime)
        return schedule_reservation(booking_id, current_datetime_str)


def schedule_reservation(booking_id, current_datetime_str):
    create_reservation_schedule_task.delay(booking_id, current_datetime_str)
    return "scheduled reservation"


# @celery.task(name='app.schedule_reservation')
def create_reservation_schedule_task(booking_id, current_datetime_str):
    app.logger.info(f"starting task: reservation for booking_id {booking_id}")
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    current_datetime = datetime.strptime(current_datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    app.logger.info(f"reservation for booking_id {booking_id} will start on {booking.earliest_reservation_datetime}")
    sleep_seconds = calculate_timedelta_in_seconds(booking.earliest_reservation_datetime, current_datetime)
    app.logger.info(f"waiting for {sleep_seconds} seconds to start reservation")
    time.sleep(sleep_seconds)
    app.logger.info(f"task executed: reservation for booking_id {booking.id}")
    return start_reservation(booking_id)


def calculate_earliest_reservation_datetime(booking):
    booking_datetime_str = booking.date_event + "T" + booking.time_event
    booking_datetime = datetime.strptime(booking_datetime_str, '%Y-%m-%dT%H:%M')
    return booking_datetime - timedelta(hours=96)


def calculate_timedelta_in_seconds(earliest_reservation_time, current_datetime):
    delta = earliest_reservation_time - current_datetime
    return delta.total_seconds()


def check_if_reservation_possible_now(booking_id, current_datetime):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    possible_now = booking.earliest_reservation_datetime <= current_datetime
    if possible_now:
        app.logger.info(f"reservation for booking_id {booking.id} possible now")
    app.logger.info(f"reservation for booking_id {booking.id} not possible yet. waiting...")
    return possible_now


def start_reservation(booking_id):
    new_reservation = Reservation(booking_id)
    db.session.add(new_reservation)
    db.session.commit()
    app.logger.info(f"reservation with reservation_id {new_reservation.id} added for booking_id {booking_id}")

    ser = Service('./chromedriver')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=options)
    booking_venue = db.session.query(Venue).join(Booking).filter_by(id=booking_id).first()
    datetime_selector = generate_datetime_selector(booking_id)

    driver.get(booking_venue.venue_url)
    date_field = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    date_field.click()
    time.sleep(2)
    apply_voucher(driver)
    complete_checkout(driver)

    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    booking.confirmation_code = get_confirmation_code(driver)

    if booking.confirmation_code is not None:
        new_reservation.status = "CONFIRMED"
        app.logger.info(f"reservation for booking_id {booking_id} confirmed")

    download_pdf(driver, booking_id)
    return new_reservation


def generate_datetime_selector(booking_id):
    date_event = db.session.query(Booking.date_event).filter_by(id=booking_id).first()[0]
    time_event = db.session.query(Booking.time_event).filter_by(id=booking_id).first()[0]
    time_event_formatted = datetime.strptime(time_event, '%H:%M')
    time_event_corrected = time_event_formatted - timedelta(hours=+1)
    datetime_selector = f".event-time[data-time='{date_event}T{time_event_corrected.time()}+00:00']"

    return datetime_selector


def apply_voucher(driver):
    voucher_field = driver.find_element(By.ID, "voucher")
    voucher_field.click()
    voucher_field.send_keys("urbansportsclub")

    voucher_submit_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-block btn-primary']")
    voucher_submit_button.click()

    add_to_cart_button = driver.find_element(By.ID, "btn-add-to-cart")
    add_to_cart_button.click()
    app.logger.info("voucher applied")
    time.sleep(2)


def complete_checkout(driver):
    try:
        checkout_url = "https://pretix.eu/Baeder/74/checkout/customer/"
        driver.get(checkout_url)

        login_radio = driver.find_element(By.ID, "input_customer_login")
        login_radio.click()
        time.sleep(2)

        website_login(driver)

        confirmation_checkbox = driver.find_element(By.ID, "input_confirm_confirm_text_0")
        confirmation_checkbox.click()
        confirmation_checkbox.send_keys(Keys.TAB)
        confirmation_checkbox.send_keys(Keys.ENTER)
        app.logger.info("checkout completed")
        time.sleep(2)

    except NoSuchElementException as error:
        app.logger.info(error)


def website_login(driver):
    user_email = driver.find_element(By.ID, "id_login-email")
    user_email.send_keys("nina.boehm1994@gmail.com")
    user_password = driver.find_element(By.ID, "id_login-password")
    user_password.send_keys("Pgvx/pF4;87$")
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.TAB)
    user_password.send_keys(Keys.ENTER)
    time.sleep(2)

    checkbox_save = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
    checkbox_save.click()
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.TAB)
    checkbox_save.send_keys(Keys.ENTER)
    app.logger.info("website login completed")
    time.sleep(2)


def get_confirmation_code(driver):
    current_url = driver.current_url
    confirmation_code = current_url[34:39]
    app.logger.info(f"confirmation code generated")
    return confirmation_code


def download_pdf(driver, booking_id):
    pdf_download_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-sm btn-primary']")
    pdf_download_button.click()
    time.sleep(8)
    app.logger.info(f"downloaded PDF for booking {booking_id}")
