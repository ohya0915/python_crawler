from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from main.forms import LoginForm, ResetPasswordForm, RegistrationForm, ChangeUserInfoForm, SendMailForm, SetPasswordForm
from models import User, VisitInfo
from __init__ import bcrypt, db, login_manager, oauth
from config import Config
from utils import password_policy_check
from main.services import check_password_service, set_password_service, forget_password_service, send_mail_service, find_user_by_set_password_code, change_visit_info_service, find_visit_by_mail, login_service, create_user_service, find_user_by_name, find_user_by_mail, find_user_by_verify_code
import uuid


main = Blueprint('main', __name__)


@login_manager.user_loader
def get_uid(uid):
    return User.query.get(uid)


def get_user_info():
    result = []
    user = None
    email = None
    try:
        user = current_user.name
        email = current_user.email
    except:
        user = session.get('username')
        email = session.get('email')
    if user:
        result.append(user)
        result.append(email)
    return False if not result else result


@main.route("/")
@main.route("/home")
def home():
    user = None
    email = None
    visit = None
    try:
        user = current_user.name
        email = current_user.email
    except:
        user = session.get('username')
        email = session.get('email')
    if email:
        visit = find_visit_by_mail(email)
    if visit:
        user = visit.name
        email = visit.email
    path = '/cat_image.jpg'
    return render_template('home.html', user=user, email=email, image=url_for("static", filename=path))

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        check_password = password_policy_check(form.password.data)
        if not check_password:
            user = find_user_by_name(form.name.data)
            if not isinstance(user, list):
                flash(f'{form.name.data} already been used!', 'warning')
                return render_template('register.html', title='Register', form=form)
            user = find_user_by_mail(form.email.data)
            if not isinstance(user, list):
                flash(f'{form.email.data} already been used!', 'warning')
                return render_template('register.html', title='Register', form=form)
            verify_code = uuid.uuid4().hex
            user = find_user_by_verify_code(verify_code)
            while user:
                verify_code = uuid.uuid4().hex
                user = find_user_by_verify_code(verify_code)
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            result = create_user_service(name=form.name.data, email=form.email.data, password=hashed_password, 
                verify_code=verify_code, active_state=Config.USER_DEFAULT_ACTIVE_STATE, where='welcome')
            if not result:
                flash('Your account has been created! You need verify email first', 'success')
                return redirect(url_for('main.login'))
            else:
                flash(result[0], 'warning')
        else:
            flash(check_password[0], 'warning')
    return render_template('register.html', title='Register', form=form)

@main.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():  
        result = login_service(name=form.name.data, password=form.password.data)
        if not result:
            return redirect(url_for('main.home'))
        else:
            flash(result[0], 'warning')
    
    return render_template('login.html', title='Login', form=form)


@main.route('/first_login/<verify_code>', methods=["GET", "POST"])
def first_login(verify_code):
    form = LoginForm()
    if form.validate_on_submit():  
        result = login_service(name=form.name.data, password=form.password.data, 
        active_state=Config.USER_START_ACTIVE_STATE, verify_code=verify_code)
        if not result:
            return redirect(url_for('main.home'))
        else:
            flash(result[0], 'warning')
    
    return render_template('login.html', title='Login', form=form)


@main.route('/resend_mail', methods=["GET", "POST"])
def send_mail():
    form = SendMailForm()
    if form.validate_on_submit():  
        result = send_mail_service(name=form.name.data, email=form.email.data, where='welcome')
        if not result:
            flash('Your welcome mail has been send', 'success')
            return redirect(url_for('main.login'))
        else:
            flash(result[0], 'warning')
    
    return render_template('resend_mail.html', form=form)


@main.route('/logout')
def logout():
    logout_user()
    session['username'] = False
    return redirect(url_for('main.login'))

@main.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    user = current_user.name
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password_check = check_password_service(current_user.password, form.current_password.data)
        if password_check:
            check_password = password_policy_check(form.password.data)
            if not check_password:
                result = set_password_service(name=user, password=form.password.data)
                if not result:
                    flash('Reset password successful!', 'success')
                    return redirect(url_for('main.home'))
                flash(result[0], 'warning')
            else:
                flash(check_password[0], 'warning')
        else:
            flash('Current password is not correct', 'warning')

    return render_template('/reset_password.html', user_info=user, form=form)


@main.route('/change_visit_info', methods=['GET', 'POST'])
def change_visit_info():
    user = get_user_info()
    if not user:
        flash('You need login first', 'warning')
        return redirect(url_for('main.login'))
    form = ChangeUserInfoForm()
    if form.validate_on_submit():
        result = change_visit_info_service(name=form.new_name.data, email=user[1])
        if not result:
            flash('Your name has been changed', 'success')
            return redirect(url_for('main.home'))
        flash(result[0], 'warning')
        
    return render_template('/change_visit_info.html', form=form)


@main.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    form = SendMailForm()
    if form.validate_on_submit():
        set_password_code = uuid.uuid4().hex
        user = find_user_by_set_password_code(set_password_code)
        while user:
            set_password_code = uuid.uuid4().hex
            user = find_user_by_set_password_code(set_password_code)
        result = forget_password_service(name=form.name.data, email=form.email.data, set_password_code=set_password_code)
        if not result:
            flash('Your mail has been send', 'success')
            return redirect(url_for('main.login'))
        flash(result[0], 'warning')
    
    return render_template('forgot_password.html', form=form)


@main.route('/set_password/<set_password_code>', methods=['GET', 'POST'])
def set_password(set_password_code):
    user = find_user_by_set_password_code(set_password_code)
    form = SetPasswordForm()
    if form.validate_on_submit():
        check_password = password_policy_check(form.password.data)
        if not check_password:
            result = set_password_service(name=user.name, password=form.password.data)
            if not result:
                flash('Your new password set successful!', 'success')
                return redirect(url_for('main.login'))
            flash(result[0], 'warning')
        flash(check_password[0], 'warning')
    return render_template('/set_password.html', user_info=user.name, form=form)


#-------Oauth-------
@main.route('/google/')
def google():
    GOOGLE_CLIENT_ID = Config.GOOGLE_OAUTH2_CLIENT_ID
    GOOGLE_CLIENT_SECRET = Config.GOOGLE_OAUTH2_SECRET
     
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('main.google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@main.route('/google/auth/')
def google_auth():
    print("current_user=======", current_user, dir(current_user))
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['username'] = user['name']
    session['email'] = user['email']
    session.permanent = True
    print(" Google User ", user)
    return redirect('/')


@main.route('/facebook/')
def facebook():
    # Facebook Oauth Config
    FACEBOOK_CLIENT_ID = Config.FACEBOOK_OAUTH2_CLIENT_ID
    FACEBOOK_CLIENT_SECRET = Config.FACEBOOK_OAUTH2_CLIENT_SECRET
    oauth.register(
        name='facebook',
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://www.facebook.com/dialog/oauth',
        authorize_params=None,
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('main.facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)
 
@main.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    session['username'] = profile['name']
    session['email'] = profile['email']
    session.permanent = True
    print("Facebook User ", profile)
    return redirect('/')


@main.route('/twitter/')
def twitter():
   
    # Twitter Oauth Config
    TWITTER_CLIENT_ID = Config.TWITTER_CLIENT_ID
    TWITTER_CLIENT_SECRET = Config.TWITTER_CLIENT_SECRET
    oauth.register(
        name='twitter',
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        request_token_url='https://api.twitter.com/oauth/request_token',
        request_token_params=None,
        access_token_url='https://api.twitter.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://api.twitter.com/oauth/authenticate',
        authorize_params=None,
        api_base_url='https://api.twitter.com/1.1/',
        client_kwargs=None,
    )
    redirect_uri = url_for('main.twitter_auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)
 
@main.route('/twitter/auth/')
def twitter_auth():
    token = oauth.twitter.authorize_access_token()
    params = {"include_email": 'true'}
    resp = oauth.twitter.get('account/verify_credentials.json', params=params)
    profile = resp.json()
    print(" Twitter User", profile)
    session['username'] = profile['name']
    session['email'] = profile['email']
    session.permanent = True
    return redirect('/')
#------------------
