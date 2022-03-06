from wtforms import Form, StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length


class RegistrationForm(Form):
    first_name = StringField("First name", [DataRequired(), Length(min=1, max=150)])
    last_name = StringField("Last name", [DataRequired(), Length(min=1, max=150)])
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class LoginForm(Form):
    email = StringField("E-mail", [DataRequired(), Length(max=150)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class VenueForm(Form):
    venue_name = StringField("Venue name", [DataRequired(), Length(max=150)])
    venue_url = StringField("Venue url", [DataRequired(), Length(max=150)])


class BookingForm(Form):
    venue_name = StringField("Venue name", [DataRequired(), Length(max=150)])
    date_event = StringField("Date", [DataRequired(), Length(max=150)])
    time_event = StringField("Time", [DataRequired(), Length(max=150)])
