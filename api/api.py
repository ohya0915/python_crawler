from __init__ import bcrypt
# import flask
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import swagger, Schema
# from flask_login import login_user
from config import Config
from flask import jsonify
# from flask import jsonify, url_for, current_app
# from async_works import USER_CREATED
from utils import password_policy_check
from main.services import check_password_service, set_password_service, forget_password_service, \
send_mail_service, find_user_by_set_password_code, find_user_by_verify_code, change_visit_info_service, \
find_visit_by_mail, login_service, create_user_service, find_user_by_name, find_user_by_mail
import uuid

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name can\'t blank')


class FileModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
        'email': {
            'type': 'string'
        },
        'verify_code': {
            'type': 'string'
        },
        'new_password': {
            'type': 'string'
        },
        'set_password_code': {
            'type': 'string'
        }
    }
    required = ['name', 'password', 'email', 'verify_code', 'new_password', 'set_password_code']


class RegisterResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Register',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'password',
                'description': '密碼, password rules: 1.Complexity: At least one lower letter(a-z),one upper letter(A-Z),one number(0-9),one special symbols(~.!@#$%^&*()_+|\{\}[];:\'\",<>?/), 2.Length:At least 8 letters',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'email',
                'description': '信箱',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Your account has been created! You need verify email first"
                    }
                }
            },
            '410': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 410,
                        'message': "Password at least {min_length} chracters"
                    }
                }
            },
            '411': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 411,
                        'message': "Passowrd does not meet complexity rules"
                    }
                }
            },
            '412': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 412,
                        'message': "{name} has been used."
                    }
                }
            },
            '413': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 413,
                        'message': "{email} has been used."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('password', type=str, required=True, help='Password can\'t blank')
        args.add_argument('email', type=str, required=True, help='Verify code can\'t blank')
        regester_args = args.parse_args()
        name = regester_args['name']
        password = regester_args['password']
        email = regester_args['email']
        min_length = Config.MINIMUM_PASSWORD_LENGTH
        check_password = password_policy_check(password)
        if not check_password:
            user = find_user_by_name(name)
            if not isinstance(user, list):
                return jsonify({'code': 412,'message': f'{name} has been used.'})
            user = find_user_by_mail(email)
            if not isinstance(user, list):
                return jsonify({'code': 413,'message': f'{email} has been used.'})
            verify_code = uuid.uuid4().hex
            user = find_user_by_verify_code(verify_code)
            while user:
                verify_code = uuid.uuid4().hex
                user = find_user_by_verify_code(verify_code)
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            result = create_user_service(name=name, email=email, password=hashed_password, 
            verify_code=verify_code, active_state=Config.USER_DEFAULT_ACTIVE_STATE, where='welcome')
            if not result:
                return jsonify({'code': 0,'message': 'Your account has been created! You need verify email first'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})     
        else:
            if check_password[0] == f"Password at least {min_length} chracters":
                return jsonify({'code': 410,'message': f"Password at least {min_length} chracters"})
            elif check_password[0] == "Passowrd does not meet complexity rules":
                return jsonify({'code': 411,'message': "Passowrd does not meet complexity rules"})
        
            

class LoginResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Login',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'password',
                'description': '密碼',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Login success"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find {name}."
                    }
                }
            },
            '401': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 401,
                        'message': "Please check your name and password."
                    }
                }
            },
            '402': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 402,
                        'message': "Please verify your email first."
                    }
                }
            },
            '403': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 403,
                        'message': "Please use the latest email to start your account."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('password', type=str, required=True, help='Password can not blank')
        login_args = args.parse_args()
        name = login_args['name']
        password = login_args['password']
        result = login_service(name=name, password=password)
        if not result:
            return jsonify({'code': 0,'message': 'Login success'})
        else:
            if result[0] == f'Can\'t find {name}.':
                return jsonify({'code': 400,'message': f'Can\'t find {name}.'})
            elif result[0] == 'Please check your account and password.':
                return jsonify({'code': 401,'message': 'Please check your account and password.'})
            elif result[0] == 'Please verify your email first.':
                return jsonify({'code': 402,'message': 'Please verify your email first.'})
            elif result[0] == 'Please use the latest email to start your account.':
                return jsonify({'code': 403,'message': 'Please use the latest email to start your account.'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})
        

class FirstLoginResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Email verify login',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'password',
                'description': '密碼',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'verify_code',
                'description': ' 信箱確認碼, 註冊後將系統(ohya0915@gmail.com)寄的信welcome mail打開後點選立刻登入系統連結，登入頁面網址的最後一串32位元字串就是信箱認證碼',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Login success"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find {name}."
                    }
                }
            },
            '401': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 401,
                        'message': "Please check your name and password."
                    }
                }
            },
            '402': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 402,
                        'message': "Please verify your email first."
                    }
                }
            },
            '403': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 403,
                        'message': "Please use the latest email to start your account."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('password', type=str, required=True, help='Password can\'t blank')
        args.add_argument('verify_code', type=str, required=True, help='Verify code can\'t blank')
        first_login_args = args.parse_args()
        name = first_login_args['name']
        password = first_login_args['password']
        verify_code = first_login_args['verify_code']
        result = login_service(name=name, password=password, active_state=Config.USER_START_ACTIVE_STATE, verify_code=verify_code)
        if not result:
            return jsonify({'code': 0,'message': 'Login success'})
        else:
            if result[0] == f'Can\'t find {name}.':
                return jsonify({'code': 400,'message': f'Can\'t find {name}.'})
            elif result[0] == 'Please check your account and password.':
                return jsonify({'code': 401,'message': 'Please check your account and password.'})
            elif result[0] == 'Please verify your email first.':
                return jsonify({'code': 402,'message': 'Please verify your email first.'})
            elif result[0] == 'Please use the latest email to start your account.':
                return jsonify({'code': 403,'message': 'Please use the latest email to start your account.'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})

 
class SendWelcomeMailResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Send welcome mail',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'email',
                'description': '信箱',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Your welcome mail has been send"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find {name}."
                    }
                }
            },
            '404': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 404,
                        'message': "Account or email is not correct."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('email', type=str, required=True, help='Email can\'t blank')
        send_mail_arg = args.parse_args()
        name = send_mail_arg['name']
        email = send_mail_arg['email']
        result = send_mail_service(name=name, email=email, where='welcome')
        if not result:
            return jsonify({'code': 0,'message': 'Your welcome mail has been send'})
        else:
            if result[0] == f'Can\'t find {name}.':
                return jsonify({'code': 400,'message': f'Can\'t find {name}.'})
            elif result[0] == 'Account or email is not correct.':
                return jsonify({'code': 404,'message': 'Account or email is not correct.'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})
        

class ResetPasswordResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Reset passwprd',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'current_password',
                'description': '舊密碼',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'new_password',
                'description': '新密碼, password rules: 1.Complexity: At least one lower letter(a-z),one upper letter(A-Z),one number(0-9),one special symbols(~.!@#$%^&*()_+|\{\}[];:\'\",<>?/), 2.Length:At least 8 letters',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Reset password successful!"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find {name}."
                    }
                }
            },
            '410': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 410,
                        'message': "Password at least {min_length} chracters"
                    }
                }
            },
            '411': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 411,
                        'message': "Passowrd doesn\'t meet complexity rules"
                    }
                }
            },
            '414': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 414,
                        'message': "Current password is not correct."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('current_password', type=str, required=True, help='Current password can\'t blank')
        args.add_argument('new_password', type=str, required=True, help='New password can\'t blank')
        reset_password_args = args.parse_args()
        name = reset_password_args['name']
        current_password = reset_password_args['current_password']
        new_password = reset_password_args['new_password']
        min_length = Config.MINIMUM_PASSWORD_LENGTH
        user = find_user_by_name(name)
        if isinstance(user, list):
            if user[0] == f'Can\'t find {name}.':
                return jsonify({'code': 400,'message': f'Can\'t find {name}.'})
            else:
                print('error:', user[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})
        password_check = check_password_service(user.password, current_password)
        if password_check:
            check_password = password_policy_check(new_password)
            if not check_password:
                result = set_password_service(name=name, password=new_password)
                if not result:
                    return jsonify({'code': 0,'message': 'Reset password successful!'})
                else:
                    print('error:', result[0])
                    return jsonify({'code': 500,'message': 'Server is busy.'})    
            else:
                if check_password[0] == f"Password at least {min_length} chracters":
                    return jsonify({'code': 410,'message': f"Password at least {min_length} chracters"})
                elif check_password[0] == "Passowrd does not meet complexity rules":
                    return jsonify({'code': 411,'message': "Passowrd doesn\'t meet complexity rules"})
        else:
            return jsonify({'code': 414,'message': 'Current password is not correct.'})


class ChangeVisitInfoResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Change visit info',
        'parameters': [
            {
                'name': 'name',
                'description': '網站上顯示的名字(非帳號)',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'email',
                'description': '信箱',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Your name has been changed"
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('email', type=str, required=True, help='Email can\'t blank')
        change_visit_info_args = args.parse_args()
        name = change_visit_info_args['name']
        email = change_visit_info_args['email']    
        result = change_visit_info_service(name=name, email=email)
        if not result:
            return jsonify({'code': 0,'message': 'Your name has been changed'})
        else:
            print('error:', result[0])
            return jsonify({'code': 500,'message': 'Server is busy.'})
        

class ForGotPasswordResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Forgot password',
        'parameters': [
            {
                'name': 'name',
                'description': '帳號',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'email',
                'description': '信箱',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Your mail has been send"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find {name}."
                    }
                }
            },
            '404': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 404,
                        'message': "Account or email is not correct."
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = parser.copy()
        args.add_argument('email', type=str, required=True, help='Email can\'t blank')
        forgot_password_args = args.parse_args()
        name = forgot_password_args['name']
        email = forgot_password_args['email']
        set_password_code = uuid.uuid4().hex
        user = find_user_by_set_password_code(set_password_code)
        while user:
            set_password_code = uuid.uuid4().hex
            user = find_user_by_set_password_code(set_password_code)
        result = forget_password_service(name=name, email=email, set_password_code=set_password_code)
        if not result:
            return jsonify({'code': 0,'message': 'Your mail has been send'})
        else:
            if result[0] == f'Can\'t find {name}.':
                return jsonify({'code': 400,'message': f'Can\'t find {name}.'})
            elif result[0] == 'Account or email is not correct.':
                return jsonify({'code': 404,'message': 'Account or email is not correct.'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})


class SetPasswordResource(Resource):
    @swagger.doc({
        'tags': ['Han\'s web'],
        'description': 'Set password',
        'parameters': [
            {
                'name': 'set_password_code',
                'description': '設定密碼驗證碼, 將系統(ohya0915@gmail.com)寄的set password mail打開點設定密碼連結, 設定密碼網址的最後一串32位元字串就是設定密碼驗證碼',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            },
            {
                'name': 'password',
                'description': '新密碼, password rules: 1.Complexity: At least one lower letter(a-z),one upper letter(A-Z),one number(0-9),one special symbols(~.!@#$%^&*()_+|\{\}[];:\'\",<>?/), 2.Length:At least 8 letters',
                'in': 'formData',
                'type': 'string',
                'required': "true"
            }
        ],
        'responses': {
            '0': {
                'description': 'Success',
                'schema': FileModel,
                'examples': {
                    'application/json': {
                        'code': 0,
                        'message': "Your new password set successful!"
                    }
                }
            },
            '400': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 400,
                        'message': "Can\'t find user."
                    }
                }
            },
            '410': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 410,
                        'message': "Password at least {min_length} chracters"
                    }
                }
            },
            '411': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 411,
                        'message': "Passowrd does not meet complexity rules"
                    }
                }
            },
            '500': {
                'description': 'Failed',
                'examples': {
                    'application/json': {
                        'code': 500,
                        'message': "Server is busy."
                    }
                }
            }
        }
    })
    def post(self):
        args = reqparse.RequestParser()
        args.add_argument('set_password_code', type=str, required=True, location=['form'], help='Set password code can\'t blank')
        args.add_argument('password', type=str, required=True, location=['form'], help='Password can\'t blank')
        set_password_args = args.parse_args()
        set_password_code = set_password_args['set_password_code']
        password = set_password_args['password']
        min_length = Config.MINIMUM_PASSWORD_LENGTH
        user = find_user_by_set_password_code(set_password_code)
        if not user:
            return jsonify({'code': 400,'message': f'Can\'t find user.'})
        check_password = password_policy_check(password)
        if not check_password:
            result = set_password_service(name=user.name, password=password)
            if not result:
                return jsonify({'code': 0,'message': 'Your new password set successful!'})
            else:
                print('error:', result[0])
                return jsonify({'code': 500,'message': 'Server is busy.'})
        else:
            if check_password[0] == f"Password at least {min_length} chracters":
                return jsonify({'code': 410,'message': f"Password at least {min_length} chracters"})
            elif check_password[0] == "Passowrd does not meet complexity rules":
                return jsonify({'code': 411,'message': "Passowrd does not meet complexity rules"})


