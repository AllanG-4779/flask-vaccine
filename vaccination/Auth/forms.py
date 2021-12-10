from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, Email


class LoginForm(FlaskForm):
    id = StringField("SSNo/IDNo/BCNo", validators=[DataRequired(
    )])

    password = PasswordField('Password', validators=[DataRequired(
        message="You cannot login without password")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EmailReset(FlaskForm):
    email = EmailField("Your Registered Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Request")


class ChangePassword(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('password', message="Password do not match")])
    submit = SubmitField("change password")
