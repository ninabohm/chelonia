from wtforms import Form, StringField, PasswordField, IntegerField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Length
from datetime import datetime


class RegistrationForm(Form):
    first_name = StringField("First name", [DataRequired(), Length(min=1, max=150)])
    last_name = StringField("Last name", [DataRequired(), Length(min=1, max=150)])
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class LoginForm(Form):
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class VenueForm(Form):
    venue_name = StringField("Venue name", validators=[DataRequired(), Length(max=150)])
    venue_url = StringField("Venue url", [DataRequired(), Length(max=150)])


class BookingForm(Form):
    venue_id = SelectField("Venue name", coerce=int, validators=[DataRequired(), Length(max=150)])
    date_event = DateField("Date", format='%Y-%m-%d', default=datetime.today, validators=[DataRequired(), Length(max=150)])
    time_event = TimeField("Time", format='%H:%M', default=datetime.now(), validators=[DataRequired(), Length(max=150)])
