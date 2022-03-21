from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Length
from datetime import datetime


class RegistrationForm(FlaskForm):
    first_name = StringField("First name", [DataRequired(), Length(min=1, max=150)])
    last_name = StringField("Last name", [DataRequired(), Length(min=1, max=150)])
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])
    venue_email = StringField("Venue E-mail", [DataRequired(), Length(max=150)])
    venue_password = PasswordField("Venue password", [DataRequired(), Length(max=150)])


class LoginForm(FlaskForm):
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class VenueForm(FlaskForm):
    venue_name = StringField("Venue name", validators=[DataRequired(), Length(max=150)])
    venue_url = StringField("Venue url", [DataRequired(), Length(max=150)])


class BookingForm(FlaskForm):
    venue_id = SelectField("Venue name", coerce=int, validators=[DataRequired(), Length(max=150)])
    datetime_event = TimeField("Date and time", format='%Y-%m-%d %H:%M', default=datetime.utcnow, validators=[DataRequired(), Length(max=150)])
