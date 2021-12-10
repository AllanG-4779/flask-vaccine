from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError
from wtforms.validators import NumberRange, DataRequired

from vaccination.models import Vaccine


class Vaccines(FlaskForm):
    name = StringField('Vaccine Name', validators=[DataRequired(message='Provide a name')])
    origin = StringField("County Origin", validators=[DataRequired(message="Where is the Country coming from?")])
    doses_req = IntegerField("Doses Required", validators=[DataRequired()])
    dose_time = IntegerField('Days before the next dose', validators=[DataRequired(message="Required"),
                                                                      NumberRange(min=0, max=4, message="Enter a reasonable number of doses")])
    submit = SubmitField('Save Vaccine')

    def validate_name(self, name):

        vaccine = Vaccine.query.filter_by(name=name.data).first()
        if vaccine:
            raise ValidationError("The vaccine is already added")

class Search(FlaskForm):
    search = StringField()
    btnsearch = SubmitField("Search")
