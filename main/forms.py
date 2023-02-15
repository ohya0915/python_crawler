from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
# from models import User


class RegistrationForm(FlaskForm):
    name = StringField('Account', validators=[DataRequired()])
    email = StringField("E-Mail", validators=[DataRequired(message="請輸入E-Mail"), Email(message="不符合E-Mail格式")], render_kw={"placeholder": "E-Mail"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "At least 8 characters."})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

   
class LoginForm(FlaskForm):
    name = StringField('Account',
                        validators=[DataRequired(), Length(min=2, max=20
                            , message='Account at least 2 characters maximum 20 characters ')], render_kw={"placeholder": "Account"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ResetPasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=8)],
                             render_kw={"placeholder": "Please input current password."})
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)],
                             render_kw={"placeholder": "At least 8 characters."})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Password is not the same.')],
                                     render_kw={"placeholder": "Confirm new password again."})
    submit = SubmitField('Reset Password')


# class ResendMailForm(FlaskForm):
#     email = StringField("E-Mail", validators=[DataRequired(message="請輸入E-Mail"), Email(message="不符合E-Mail格式")], render_kw={"placeholder": "E-Mail"})
    
#     submit = SubmitField('Send')

class SetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)],
                             render_kw={"placeholder": "At least 8 characters."})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Password is not the same.')],
                                     render_kw={"placeholder": "Confirm new password again."})
    submit = SubmitField('Reset Password')


class ChangeUserInfoForm(FlaskForm):
    new_name = StringField('New Name', validators=[DataRequired(), Length(max=60)],
                             render_kw={"placeholder": "Please input your name.(This won\'t change your account.)"})
    
    submit = SubmitField('Change')


class SendMailForm(FlaskForm):
    name = StringField('Account', validators=[DataRequired()])
    email = StringField("E-Mail", validators=[DataRequired(message="請輸入E-Mail"), Email(message="不符合E-Mail格式")], render_kw={"placeholder": "E-Mail"})
    
    submit = SubmitField('Send')