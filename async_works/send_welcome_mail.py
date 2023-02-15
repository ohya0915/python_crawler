from flask import current_app
from . import USER_CREATED, USER_FORGOT_PASSWORD
from utils import create_mail_message, send_mail


@USER_CREATED.connect
def send_welcome_mail(sender, **kwargs):
    recipient = kwargs["recipient"]
    print('kwargs=======', kwargs)
    msg = create_mail_message(to=recipient,
                              subject="【 Hans's web 】Welcome Mail",
                              text=None,
                              template="user_created.html",
                              **kwargs
                              )
    send_mail(msg)


@USER_FORGOT_PASSWORD.connect
def send_set_password_mail(sender, **kwargs):
    recipient = kwargs["recipient"]
    print('kwargs=======', kwargs)
    msg = create_mail_message(to=recipient,
                              subject="【 Hans's web 】Set Password Mail",
                              text=None,
                              template="user_forgot_password.html",
                              **kwargs
                              )
    send_mail(msg)

