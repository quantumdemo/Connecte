from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class PlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired()])
    price = IntegerField('Price (in Kobo)', validators=[DataRequired(), NumberRange(min=0)])
    features = TextAreaField('Features (one per line)', validators=[DataRequired()])
    submit = SubmitField('Save Plan')