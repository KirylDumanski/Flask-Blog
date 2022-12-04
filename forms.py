from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, StringField, SubmitField, IntegerField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email()])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField("Remember me", default=False)
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name: ", validators=[Length(min=4, max=100)])
    age = IntegerField()
    city = StringField("City: ", validators=[Length(max=100)])
    email = StringField("Email: ", validators=[Email()])
    password1 = PasswordField("Password: ", validators=[DataRequired(), Length(min=4, max=100)])
    password2 = PasswordField("Confirm password: ",
                              validators=[DataRequired(), EqualTo('password1', message='Passwords do not match.')])
    submit = SubmitField("Sign up")
