from __init__ import api
from api.api import RegisterResource, LoginResource, FirstLoginResource, SendWelcomeMailResource, \
ResetPasswordResource, ChangeVisitInfoResource, ForGotPasswordResource, SetPasswordResource

api.add_resource(RegisterResource, '/ohya/register')
api.add_resource(LoginResource, '/ohya/login')
api.add_resource(FirstLoginResource, '/ohya/first_login')
api.add_resource(SendWelcomeMailResource, '/ohya/send_welcome_mail')
api.add_resource(ResetPasswordResource, '/ohya/reset_password')
api.add_resource(ChangeVisitInfoResource, '/ohya/change_visit_info')
api.add_resource(ForGotPasswordResource, '/ohya/forgot_password')
api.add_resource(SetPasswordResource, '/ohya/set_password')

