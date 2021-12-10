from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


from vaccination.models import User, Vaccine


class Registration(FlaskForm):
    id = StringField(
        "SSNo/IDNo/BCNo", validators=[DataRequired(),  Length(min=6, max=10)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[
                        DataRequired(), Length(min=9, max=13)])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, max=50, message="Length should be between 8 and 50")])
    confirm = PasswordField('Confirm Password', validators=[EqualTo(
        fieldname='password', message="Passwords Do not match")])
    submit = SubmitField('Register')
    # Custom validation for user existing

    def validate_id(self, id):
        # Check if the user exist and select the first matching value
        user = User.query.filter_by(id=id.data).first()
        if user:
            raise ValidationError("This user ID is taken")

    def validate_email(self, email):
        # Check if the user exist and select the first matching value
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email address already in use")


class Profile(FlaskForm):
    firstname = StringField("First Name", validators=[
                            DataRequired(message="Please provide a name")])
    lastname = StringField("Other Name(s)", validators=[
                           DataRequired(message="Please provide a name")])
    dob = DateField("Date of Birth", validators=[
                    DataRequired(message="Date of birth is required")])
    county = SelectField("Region", validators=[DataRequired(message="Select county")],
                         choices=[
        ("Nairobi", "Nairobi"), ('Nyanza', "Nyanza"),
        ('North Eastern', 'North Estern'), ("Coast", "Coast"), ("Central", "Central"), ("Eastern", "Eastern"), ("Western", "Western")]
    )
    complete = SubmitField("Complete profile")

class LoginForm(FlaskForm):
    id = StringField("SSNo/IDNo/BCNo", validators=[DataRequired(
    )])

    password = PasswordField('Password', validators=[DataRequired(
        message="You cannot login without password")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
class Vaccines(FlaskForm):
    name = StringField('Vaccine Name', validators=[DataRequired(message='Provide a name')])
    origin = StringField("County Origin", validators=[DataRequired(message="Where is the Country coming from?")])
    doses_req = IntegerField("Doses Required", validators=[DataRequired()])
    dose_time = IntegerField('Days before the next dose', validators=[DataRequired()])
    submit = SubmitField('Save Vaccine')

    def validate_name(self, name):

        vaccine = Vaccine.query.filter_by(name=name.data).first()
        if vaccine:
            raise ValidationError("The vaccine is already added")

class Search(FlaskForm):
    search = StringField()
    btnsearch = SubmitField("Search")

class EmailReset(FlaskForm):
    email = EmailField("Your Registered Email" , validators=[DataRequired(), Email()])
    submit = SubmitField("Send Request")
    
class ChangePassword(FlaskForm):
    password = PasswordField("New Password" , validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators = [EqualTo('password', message="Password do not match")])
    submit = SubmitField("change password")
