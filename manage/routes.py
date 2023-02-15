
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user
from config import Config
from models import User
from main.services import find_all_user, delete_user_service

ohyamanage = Blueprint('ohyamanage', __name__)


@ohyamanage.route("/manage", methods=['GET', 'POST'])
def manage():
    if current_user.is_authenticated:
        if current_user.role != Config.ROLE_MANAGER:
            flash('You are not allow into manage!', 'warning')
            return redirect(url_for('main.home'))
        result = find_all_user()
    else :
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))
    return render_template('manage.html', result=result)

@ohyamanage.route("/manage/<int:id>", methods=['GET', 'POST'])
def manage_delete(id):
    result = delete_user_service(id)
    if not result:
        flash('Delete account successful!', 'success')
        return  redirect(url_for('ohyamanage.manage'))
    else:
        flash(result[0], 'warning')
        return  redirect(url_for('ohyamanage.manage'))

    