from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class StockForm(FlaskForm):
    target_year = StringField('Target Year: (ex:2019)', validators=[DataRequired()])
    search_stock = StringField('Search For: (ex:2330)', validators=[DataRequired()])
    submit = SubmitField('Go')

class StockSelectForm(FlaskForm):
    choices = [('high', 'High'),
               ('low', 'Low'),
               ('open', 'Open'),
               ('close', 'Close'),
               ('volume', 'Volume'),
               ('adj_close', 'Adj Close')]
    select = SelectField('Choose one : ', choices=choices)
    submit = SubmitField('Plot')

