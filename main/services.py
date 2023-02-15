from flask import current_app, url_for
from flask_login import login_user
from models import User, VisitInfo
from async_works import USER_CREATED, USER_FORGOT_PASSWORD
from __init__ import bcrypt, db
from config import Config


# find user ------
def find_all_user():
    result = []
    try:
        user = User.query.all()
        return user
    except Exception as e:
        result.append(e)
        return result


def find_user_by_id(id):
    result = []
    try:
        user = User.query.get(id)
        return user
    except Exception as e:
        result.append(e)
        return result


def find_user_by_name(name):
    result = []
    try:
        user = User.query.filter_by(name=name).first()
        if not user:
            result.append(f'Can\'t find {name}.')
            return result
        return user
    except Exception as e:
        result.append(e)
        return result


def find_user_by_mail(email):
    result = []
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            result.append(f'Can\'t find {email}.')
            return result
        return user
    except Exception as e:
        result.append(e)
        return result


def find_user_by_set_password_code(set_password_code):
    result = []
    try:
        user = User.query.filter_by(set_password_code=set_password_code).first()
        return user
    except Exception as e:
        result.append(e)
        return result


def find_user_by_verify_code(verify_code):
    result = []
    try:
        user = User.query.filter_by(verify_code=verify_code).first()
        return user
    except Exception as e:
        result.append(e)
        return result


def find_visit_by_mail(email):
    result = []
    try:
        visit = VisitInfo.query.filter_by(email=email).first()
        return visit
    except Exception as e:
        result.append(e)
        return result
#------------------

# password ------
def check_password_service(database_password, current_password):
    if bcrypt.check_password_hash(database_password, current_password):
        return True
    else:
        return False


def set_password_service(name, password):
    result = []
    try:
        user = find_user_by_name(name)
        if isinstance(user, list):
            result.append(user[0])
            return result
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
    except Exception as e:
        result.append(e)
        return result


def forget_password_service(name, email, set_password_code):
    result = []
    user = check_name_mail(name, email)
    if isinstance(user, list):
        result.append(user[0])
        return result   
    else:
        try:
            user.set_password_code = set_password_code
            db.session.commit()
            result = send_mail_service(name, email, 'forgot')
            if result:
                return result
        except Exception as e:
            result.append(e)
            return result
#------------------

def login_service(name, password, active_state=None, verify_code=None):
    result = []
    user = find_user_by_name(name)
    if isinstance(user, list):
        result.append(user[0])
        return result
    else:
        if active_state and verify_code:
            if verify_code != user.verify_code:
                result.append('Please use the latest email to start your account.')
                return result
            user.active_state = active_state
            db.session.add(user)    
            db.session.commit()
        try:
            if user and bcrypt.check_password_hash(user.password, password):
                if user.active_state == Config.USER_DEFAULT_ACTIVE_STATE:
                    result.append('Please verify your email first.')
                    return result      
                login_user(user)
                
            else:
                result.append('Please check your account and password.')
                return result 
        except Exception as e:
            result.append(e)
            return result 
    

def create_user_service(name, email, password, verify_code, active_state, where):
    result = []
    try:
        user = User(name=name, email=email, password=password, verify_code=verify_code, 
                active_state=active_state)
        db.session.add(user)
        db.session.commit()
        send_mail_service(name=name, email=email, where=where)
    except Exception as e:
        result.append(e)
        return result


def change_visit_info_service(name, email):
    result = []
    visit = find_visit_by_mail(email)
    if isinstance(visit, list):
        result.append(visit[0])
        return result
    else:
        try:
            if visit:
                visit.name = name
                db.session.commit()
                return False
            visit = VisitInfo(name=name, email=email)
            db.session.add(visit)
            db.session.commit()
        except Exception as e:
            result.append(e)
            return result


def delete_user_service(id):
    result = []
    try:
        user = find_user_by_id(id)
        if user.role != Config.ROLE_MANAGER:
            db.session.delete(user)
            db.session.commit()
        else:
            result.append('You can\'t delete me!')
            return result
    except Exception as e:
        result.append(e)
        return result


def check_name_mail(name, email):
    result = []
    try:
        user = find_user_by_name(name)
        if isinstance(user, list):
            result.append(user[0])
            return result
        else:
            if user.email != email:
                result.append('Account or email is not correct.')
                return result
            return user
    except Exception as e:
        result.append(e)
        return result


def send_mail_service(name, email, where):
    result = []
    user = check_name_mail(name, email)
    if isinstance(user, list):
        result.append(user[0])
        return result    
    else:   
        if where == 'forgot':
            try:
                USER_FORGOT_PASSWORD.send(current_app._get_current_object(),
                    name=name,
                    email=email,
                    reset_url=url_for("main.set_password", set_password_code=user.set_password_code, _external=True),
                    recipient=email)
            except Exception as e:
                result.append(e)
                return result
        elif where == 'welcome':
            try:
                USER_CREATED.send(current_app._get_current_object(),
                    name=name,
                    email=email,
                    login_url=url_for("main.first_login", verify_code=user.verify_code, _external=True),
                    recipient=email)
            except Exception as e:
                result.append(e)
                return result
    
