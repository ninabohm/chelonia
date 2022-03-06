from wtforms import Form, StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length


class RegistrationForm(Form):
    first_name = StringField("First name", [DataRequired(), Length(min=1, max=20)])
    last_name = StringField("Username", [DataRequired(), Length(min=1, max=20)])
    email = StringField("E-mail", [DataRequired(), Length(max=20)])
    password = PasswordField("Password", [DataRequired(), Length(max=150)])


class LoginForm(Form):
    email = StringField("E-mail", [DataRequired(), Length(max=20)])
    password = PasswordField("Password", [DataRequired(), Length(max=30)])

