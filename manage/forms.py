from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, BooleanField


class UserVerifyEditForm(FlaskForm):
    uid = IntegerField('uid')
    id_card = BooleanField('id_card')
    bill = BooleanField('bill')
    phone = BooleanField('phone')
    email = BooleanField('email')

class UserVerifySearchForm(FlaskForm):
    choices = [('uid', 'User ID'),         #左邊是對應route,右邊是顯示的樣子
               ('email', 'E-mail'),     #下拉式選單
               ('phone', 'Phone'),
               ('id_card', 'ID card'),
               ('bill', 'Bill')]
    select = SelectField('Search for User Verify:', choices=choices)
    search = StringField('')

class UserVerifyTypeChoseForm(FlaskForm):
    choices = [('email', 'E-mail'),         #左邊是對應route,右邊是顯示的樣子
               ('phone', 'Phone'),     #下拉式選單
               ('id_card', 'ID_card'),
               ('bill', 'Bill')]
    select = SelectField('Select for type:', choices=choices)
    search = StringField('')