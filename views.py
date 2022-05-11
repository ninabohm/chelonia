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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, g, render_template, request, redirect, flash, url_for, session, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from model.models import db, Booking, User, Venue, Ticket
from forms.forms import RegistrationForm, LoginForm, VenueForm, BookingForm
from datetime import datetime, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def requires_not_logged_in(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        if "first_name" not in session:
            return func(*args, **kwargs)
        return redirect(url_for('create_booking'))
    return wrapped_func


@app.route('/')
def index():
    return redirect(url_for("create_booking"))


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
        user.birthday = request.form.get('birthday')
        user.street = request.form.get('street')
        user.house_no = request.form.get('house_no')
        user.postal_code = request.form.get('postal_code')
        user.city = request.form.get('city')
        user.phone = request.form.get('phone')
        user.urban_sports_membership_no = request.form.get('urban_sports_membership_no')
        try:
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"added user {user.first_name} {user.last_name} to db")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            message = "An account with this email already exists. Please try again"
            app.logger.info(f"couldn't register user {user.first_name} {user.last_name}")
            return render_template("register.html", form=form, error=message)
    return render_template("register.html", form=form)


@app.route("/user/account", methods=['GET'])
@login_required
def account():
    return render_template("account.html", user=current_user)


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
            return redirect(url_for('create_booking'))
        message = "Password and email don't match or user doesn't exist"
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
        venue_type = request.form.get("venue_type")
        venue = Venue(venue_name, venue_url, venue_type)
        db.session.add(venue)
        db.session.commit()
        app.logger.info(f"added venue, name: {venue.venue_name}, id: {venue.id}, venue_type: {venue_type}")
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
            'venue_type': venue.venue_type,
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
        booking.earliest_ticket_datetime = booking.earliest_ticket_datetime.astimezone(pytz.timezone('CET'))
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
    return render_template("bookings.html", bookings=bookings, user=current_user)


@app.route('/booking/<booking_id>')
@login_required
def get_booking_by_id(booking_id):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    data = []
    booking.datetime_event = booking.datetime_event.astimezone(pytz.timezone('CET'))
    booking.earliest_ticket_datetime = booking.earliest_ticket_datetime.astimezone(pytz.timezone('CET'))
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
    return render_template("booking_show.html", booking=booking)


@app.route('/booking/create', methods=['GET', 'POST'])
@login_required
def create_booking():
    available_venues = db.session.query(Venue).all()
    venue_choices = [(item.id, item.venue_name) for item in available_venues]
    form = BookingForm()
    form.venue_id.choices = venue_choices
    if request.method == 'POST':
        booking = get_booking_from_form()
        create_ticket(booking.id)
        return render_template("booking_show.html", booking=booking)
    return render_template("create_booking.html", form=form)


def get_booking_from_form():
    venue_id = request.form.get("venue_id")
    date_event = request.form.get("date_event")
    time_event = request.form.get("time_event")
    app.logger.info("collected booking data from form")
    booking = post_booking_and_save(venue_id, date_event, time_event)
    return booking


def post_booking_and_save(venue_id, date_event, time_event):
    datetime_event_utc = change_to_correct_timezone(date_event, time_event)
    booking = Booking(venue_id, datetime_event_utc, current_user.id)
    booking.earliest_ticket_datetime = calculate_earliest_ticket_datetime(booking)
    db.session.add(booking)
    db.session.commit()
    app.logger.info(f"added booking: id {booking.id}, venue_id: {booking.venue_id}, datetime: {booking.datetime_event}, earliest_ticket_datetime: {booking.earliest_ticket_datetime}")
    return booking


def change_to_correct_timezone(date_event, time_event):
    tz = timezone("Europe/Berlin")
    datetime_event_naive = datetime.strptime(date_event + " " + time_event, "%Y-%m-%d %H:%M")
    datetime_event_berlin = tz.localize(datetime_event_naive)
    datetime_event_utc = datetime_event_berlin.astimezone(pytz.UTC)
    datetime_event_removed = datetime_event_utc.replace(tzinfo=None)
    app.logger.info(f"datetime_event: {datetime_event_naive} naive, {datetime_event_berlin} Berlin time, {datetime_event_utc} UTC, {datetime_event_removed} (removed timezone)")
    return datetime_event_removed


@app.route('/ticket')
@login_required
def get_tickets():
    tickets = db.session.query(Ticket).all()
    data = []
    for ticket in tickets:
        obj = {
            'id': ticket.id,
            'booking_id': ticket.booking_id,
            'created_at': ticket.created_at,
            'user_id': ticket.user_id,
            'status': ticket.status
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
    return render_template("tickets.html", tickets=tickets, user=current_user)


@app.route('/ticket/<booking_id>', methods=['POST'])
@login_required
def create_ticket(booking_id):
    venue_type = db.session.query(Venue.venue_type).join(Booking).filter_by(id=booking_id).first()[0]
    if venue_type == "bouldering":
        if check_if_ticket_possible_now(booking_id, datetime.utcnow()):
            return start_ticket_bouldering(booking_id)
        app.logger.info("here comes the scheduler")

    if venue_type == "swimming":
        if check_if_ticket_possible_now(booking_id, datetime.utcnow()):
            return start_ticket_swimming(booking_id, current_user.id)
        schedule_ticket(booking_id, str(datetime.utcnow()), current_user.id)


def start_ticket_bouldering(booking_id):
    ticket = Ticket(booking_id, current_user.id)
    db.session.add(ticket)
    db.session.commit()
    app.logger.info(f"added ticket, id: {ticket.id}, user: {current_user.id}")

    driver = initialize_chrome_driver()
    open_venue_website(driver, booking_id)

    try:
        choose_ticket_slot_bouldering(driver, booking_id)
        enter_user_data(driver)
        accept_privacy_and_book(driver)
        if "Glückwunsch" in driver.page_source:
            ticket.status = "CONFIRMED"
            db.session.commit()
    except NoSuchElementException:
        app.logger.info(f"an error occured, aborting, {NoSuchElementException}")
        ticket.status = "ABORTED"
        db.session.commit()
        return
    return ticket


def choose_ticket_slot_bouldering(driver, booking_id):
    next_button = driver.find_element(By.CSS_SELECTOR, ".drp-course-month-selector-next")
    if check_if_next_month(booking_id):
        next_button.click()
    date_selector = generate_datetime_selector(booking_id)
    date_field = driver.find_element(By.XPATH, date_selector)
    date_field.click()
    click_booking_button(driver, booking_id, next_button)
    time.sleep(1)
    app.logger.info("ticket slot chosen")



def enter_user_data(driver):
    driver.find_element(By.NAME, "first-name").send_keys(current_user.first_name)
    app.logger.info(f"entered first name: {current_user.first_name}")
    driver.find_element(By.NAME, "last-name").send_keys(current_user.last_name)
    app.logger.info(f"entered last name: {current_user.last_name}")
    driver.find_element(By.NAME, "email").send_keys(current_user.venue_email)
    app.logger.info(f"entered venue_email")

    driver.find_element(By.CSS_SELECTOR, "option[value='155589630']").click()
    driver.find_element(By.NAME, "participant-additional-field-value").send_keys(current_user.urban_sports_membership_no)
    app.logger.info(f"entered urban_sports_membership_no")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    app.logger.info("user data entered")


def accept_privacy_and_book(driver):
    privacy_field = driver.find_element(By.XPATH, "//input[@id='drp-booking-data-processing-cb']")
    privacy_field.click()
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(1)
    app.logger.info("privacy accepted and booking finalized")


def click_booking_button(driver, booking_id, next_button):
    iterator = ActionChains(driver).move_to_element(next_button)
    count = calc_quarter_count(booking_id)
    for x in range(0, count):
        iterator.send_keys(Keys.TAB).perform()
    iterator.send_keys(Keys.ENTER).perform()
    app.logger.info(f"clicked booking button at position {count}")


def calc_quarter_count(booking_id):
    minutes = calc_minutes(booking_id)
    count = int(minutes / 15 + 1)
    return count


def check_if_next_month(booking_id):
    booking_created = db.session.query(Booking.created_at).filter_by(id=booking_id).first()[0]
    booking_date = db.session.query(Booking.datetime_event).filter_by(id=booking_id).first()[0]
    if booking_date.month == booking_created.month:
        return False
    app.logger.info("booking_date next month, changing calendar view")
    return True


def calc_minutes(booking_id):
    booking_datetime = db.session.query(Booking.datetime_event).filter_by(id=booking_id).first()[0]
    minutes = booking_datetime.minute
    hours_normalized = booking_datetime - timedelta(hours=14)
    total_minutes = hours_normalized.hour * 60 + minutes
    app.logger.info(f"total_minutes: {total_minutes}")
    return total_minutes


def schedule_ticket(booking_id, current_datetime_str, current_user_id):
    create_ticket_schedule_task.delay(booking_id, current_datetime_str, current_user_id)


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
    start_ticket_swimming(booking_id, current_user_id)


def calculate_earliest_ticket_datetime(booking):
    result = db.session.query(Venue.venue_type).filter_by(id=booking.venue_id)
    for venue_type, in result:
        if venue_type == "bouldering":
            delta = timedelta(days=7)
            local = booking.datetime_event - delta
            app.logger.info(f"venue_type: {venue_type}, timedelta: {delta}")
            return local.astimezone(pytz.UTC)
    delta = timedelta(hours=96)
    local = booking.datetime_event - delta
    app.logger.info(f"venue_type {venue_type}, timedelta: {delta}")
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


def start_ticket_swimming(booking_id, current_user_id):
    ticket = Ticket(booking_id, current_user.id)
    db.session.add(ticket)
    db.session.commit()

    app.logger.info(f"started ticket: id: {ticket.id}, booking_id: {booking_id}, user id: {current_user_id}")

    driver = initialize_chrome_driver()

    try:
        choose_ticket_slot_swimming(driver, booking_id)
        apply_voucher(driver)
        complete_checkout(driver, booking_id)
    except NoSuchElementException:
        app.logger.info("ticket slot not available, aborting")
        ticket.status = "ABORTED"
        db.session.commit()
        return

    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    booking.confirmation_code = get_confirmation_code(driver)

    if booking.confirmation_code is not None and not "re_co":
        ticket.status = "CONFIRMED"
        db.session.commit()
        download_pdf(driver, booking_id)
        app.logger.info("pdf downloaded")
    app.logger.info("an error occurred")

    return ticket


def initialize_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=chrome_options)
    app.logger.info(f"initialized chrome driver")
    return driver


def choose_ticket_slot_swimming(driver, booking_id):
    datetime_selector = generate_datetime_selector(booking_id)
    date_field = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    date_field.click()
    time.sleep(2)
    app.logger.info("ticket slot chosen")


def open_venue_website(driver, booking_id):
    booking_venue = db.session.query(Venue).join(Booking).filter_by(id=booking_id).first()
    driver.get(booking_venue.venue_url)
    app.logger.info("venue website opened")


def generate_datetime_selector(booking_id):
    booking = db.session.query(Booking).filter_by(id=booking_id).first()
    result = db.session.query(Venue.venue_type).filter_by(id=booking.venue_id)
    for venue_type, in result:
        if venue_type == "bouldering":
            return f"//div[normalize-space()='{booking.datetime_event.date().day}']"
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
