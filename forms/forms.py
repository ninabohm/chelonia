from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, DateField, TimeField, RadioField
from wtforms.validators import DataRequired, Length
from datetime import datetime


class RegistrationForm(FlaskForm):
    first_name = StringField("First name", [DataRequired(), Length(min=1, max=150)])
    last_name = StringField("Last name", [DataRequired(), Length(min=1, max=150)])
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])
    venue_email = StringField("Venue E-mail", [DataRequired(), Length(max=150)])
    venue_password = PasswordField("Venue password", [DataRequired(), Length(max=150)])
    birthday = DateField("Birthday", [DataRequired(), Length(min=1, max=150)])
    street = StringField("Street", [DataRequired(), Length(min=1, max=150)])
    house_no = StringField("House number", [DataRequired(), Length(min=1, max=150)])
    postal_code = StringField("Postal code", [DataRequired(), Length(min=1, max=150)])
    city = StringField("City", [DataRequired(), Length(min=1, max=150)])
    phone = StringField("Phone", [DataRequired(), Length(min=1, max=150)])
    urban_sports_membership_no = StringField("Urban Sports Club membership number", [Length(max=150)])


class LoginForm(FlaskForm):
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class VenueForm(FlaskForm):
    venue_name = StringField("Venue name", validators=[DataRequired(), Length(max=150)])
    venue_url = StringField("Venue url", [DataRequired(), Length(max=150)])
    venue_type = RadioField("Type", choices=[("bouldering", "bouldering"), ("swimming", "swimming")])


class BookingForm(FlaskForm):
    venue_id = SelectField("Venue name", coerce=int, validators=[DataRequired(), Length(max=150)])
    date_event = DateField("Date", format='%Y-%m-%d', default=datetime.today, validators=[DataRequired(), Length(max=150)])
    time_event = TimeField("Time", format='%H:%M', default=datetime.now(), validators=[DataRequired(), Length(max=150)])
