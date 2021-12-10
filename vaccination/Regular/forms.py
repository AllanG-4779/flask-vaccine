from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from vaccination.models import User



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
