from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class TargetStockForm(FlaskForm):
    target_year = StringField('Target Year: (ex:2023)', validators=[DataRequired()])
    target_month = StringField('Target Month: (ex:1)', validators=[DataRequired()])
    target_stock = StringField('Search For: (ex:2330)', validators=[DataRequired()])
    submit = SubmitField('產生csv')
