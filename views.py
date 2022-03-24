from app import app, login_manager, celery
import time
import json
import os
import pytz
from pytz import timezone
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask import Flask, g, render_template, request, redirect, flash, url_for, session, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from model.models import db, Booking, User, Venue, Ticket
from forms.forms import RegistrationForm, LoginForm, VenueForm, BookingForm
from datetime import datetime, timedelta



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def requires_logged_in(func):
  @wraps(func)
  def wrapped_func(*args, **kwargs):
      form = LoginForm()
      if "first_name" in session:
          return func(*args, **kwargs)
      return redirect(url_for('login'))
  return wrapped_func


def requires_not_logged_in(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if "first_name" not in session:
            return func(*args, **kwargs)
        return redirect(url_for('create_booking'))
    return wrapped_func


@app.route('/')
def index():
    try:
        user_first_name = current_user.first_name
    except AttributeError:
        user_first_name = ""
    return render_template("index.html", user_first_name=user_first_name)


@app.route('/protected')
@login_required
def protected():
    return "protected route"


@app.route('/protected-2')
@requires_logged_in
def protected2():
    return "protected route 2"


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
        user.venue_email = request.form.get('venue_email')
        user.venue_password = request.form.get('venue_password')
        try:
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"added user {user.first_name} {user.last_name} with id {user.id} to db")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            message = "An account with this email already exists. Please try again"
            return render_template("register.html", form=form, error=message)
    return render_template("register.html", form=form)


@app.route("/user/account", methods=['GET'])
@login_required
def account():
    return render_template("account.html", user_first_name=current_user.first_name)


@app.route('/user')
@login_required
def get_users():
    users = db.session.query(User).all()
    data = []
    for user in users:
        obj = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'bookings': user.bookings
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
    return render_template('users.html', users=data)


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
        message = "Password and email do not match or user does not exist"
        return render_template("login.html", form=form,  message=message)
    return render_template("login.html", form=form)


@app.route('/user/logout', methods=['GET', 'POST'])
def logout():
    app.logger.info(f"logging out user {current_user.id}")
    logout_user()
    session.clear()
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
        booking.datetime_event = booking.datetime_event.astimezone(pytz.timezone('CET'))
        obj = {
            'id': booking.id,
            'venue_id': booking.venue_id,
            'datetime_event': booking.datetime_event,
            'user_id': booking.user_id,
            'created_at': booking.created_at,
            'confirmation_code': booking.confirmation_code,
            'ticket': booking.ticket
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
        booking = post_booking_and_save(venue_id, date_event, time_event)
        create_ticket(booking.id)
        return render_template("booking_show.html", booking=booking)
    return render_template("create_booking.html", form=form)


def post_booking_and_save(venue_id, date_event, time_event):
    datetime_event_cet = datetime.strptime(date_event + " " + time_event, "%Y-%m-%d %H:%M").replace(tzinfo=timezone("CET"))
    datetime_event_utc = datetime_event_cet.astimezone(pytz.UTC)
    app.logger.info(f"datetime_event_utc: {datetime_event_utc}")
    booking = Booking(venue_id, datetime_event_utc, current_user.id)
    #booking = Booking(venue_id, datetime_event_utc, "3")
    booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(booking)
    db.session.add(booking)
    db.session.commit()
    app.logger.info(f"added booking: id {booking.id}, venue_id: {booking.venue_id}, datetime: {booking.datetime_event}, earliest_ticket_datetime: {booking.earliest_ticket_datetime}")
    return booking


@app.route('/booking/<booking_id>')
@login_required
def get_booking_by_id(booking_id):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    data = [
        {
            'id': booking.id,
            'venue_id': booking.venue_id,
            'datetime_event': booking.datetime_event,
            'user_id': booking.user_id,
            'created_at': booking.created_at,
            'confirmation_code': booking.confirmation_code,
            'ticket_status': booking.ticket
        }
    ]
    response = app.response_class(
        response=json.dumps(data, default=str),
        status=200,
        mimetype='application/json'
    )
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        return response
    return render_template("booking_show.html", booking=booking)


@app.route('/ticket')
@login_required
def get_tickets():
    tickets = []
    for item in db.session.query(Ticket).all():
        tickets.append(item)
    return render_template("tickets.html", tickets=tickets)


@app.route('/ticket/<booking_id>', methods=['GET', 'POST'])
@login_required
def create_ticket(booking_id):
    if request.method == 'POST':
        current_datetime = datetime.utcnow()
        ticket = Ticket(booking_id, current_user.id)
        db.session.add(ticket)
        db.session.commit()

        if check_if_ticket_possible_now(booking_id, current_datetime):
            start_ticket(booking_id, current_user.id)
            return render_template("ticket_show.html", ticket=ticket)
        current_datetime_str = str(current_datetime)
        schedule_ticket(booking_id, current_datetime_str, current_user.id)

        booking = db.session.query(Booking).filter_by(id=booking_id)
        return render_template("ticket_scheduled.html", ticket=ticket, booking=booking)


def schedule_ticket(booking_id, current_datetime_str, current_user_id):
    create_ticket_schedule_task.delay(booking_id, current_datetime_str, current_user_id)
    return "successfully scheduled ticket"


@celery.task(name='app.schedule_ticket')
def create_ticket_schedule_task(booking_id, current_datetime_str, current_user_id):
    app.logger.info(f"creating task: ticket for booking_id {booking_id}")
    current_datetime = datetime.strptime(current_datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    app.logger.info(f"current_datetime: {current_datetime}")
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    app.logger.info(f"ticket for booking_id: {booking_id} will start on {booking.earliest_ticket_datetime}")
    sleep_seconds = calculate_timedelta_in_seconds(booking.earliest_ticket_datetime, current_datetime)
    app.logger.info(f"sleep seconds: {sleep_seconds}")
    time.sleep(sleep_seconds)
    #time.sleep(20)
    start_ticket(booking_id, current_user_id)


def calculate_earliest_ticket_datetime(booking):
    local = booking.datetime_event - timedelta(hours=96)
    return local.astimezone(pytz.UTC)


def calculate_timedelta_in_seconds(earliest_ticket_time, current_datetime):
    delta = earliest_ticket_time - current_datetime
    return delta.total_seconds()


def check_if_ticket_possible_now(booking_id, current_datetime):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    possible_now = booking.earliest_ticket_datetime <= current_datetime
    if not possible_now:
        app.logger.info(f"ticket for booking_id: {booking.id} not possible yet. scheduling for later...")
    return possible_now


def start_ticket(booking_id, current_user_id):
    ticket = db.session.query(Ticket).join(Booking).filter_by(id=booking_id).first()
    app.logger.info(f"started ticket: id: {ticket.id}, booking_id: {booking_id}, user id: {current_user_id}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # TODO: save headless as env var for local debugging
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=chrome_options)
    app.logger.info(f"initialized chrome driver")

    choose_ticket_slot(driver, booking_id)
    # if 'presale' in driver.page_source:
    #    app.logger.info("ticket not selectable yet")
    #    return
    apply_voucher(driver)
    complete_checkout(driver, booking_id)

    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    booking.confirmation_code = get_confirmation_code(driver)

    if booking.confirmation_code is not None and not "re_co":
        ticket.status = "CONFIRMED"
        db.session.commit()
        download_pdf(driver, booking_id)
        app.logger.info("pdf downloaded")


def choose_ticket_slot(driver, booking_id):
    booking_venue = db.session.query(Venue).join(Booking).filter_by(id=booking_id).first()
    datetime_selector = generate_datetime_selector(booking_id)
    driver.get(booking_venue.venue_url)
    date_field = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    date_field.click()
    app.logger.info("ticket slot chosen")
    time.sleep(2)


def generate_datetime_selector(booking_id):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    return f".event-time[data-time='{booking.datetime_event.date()}T{booking.datetime_event.time()}+00:00']"


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


def complete_checkout(driver, booking_id):
    venue_url = db.session.query(Venue.venue_url).join(Booking).filter_by(id=booking_id).first()[0]
    checkout_url = f"{venue_url}checkout/customer/"
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


def website_login(driver):
    user_email = driver.find_element(By.ID, "id_login-email")
    user_email.send_keys(current_user.venue_email)
    user_password = driver.find_element(By.ID, "id_login-password")
    user_password.send_keys(current_user.venue_password)
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
