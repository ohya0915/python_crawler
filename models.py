from flask_login import UserMixin
from __init__ import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, comment="資料索引")
    name = db.Column(db.String(60), unique=True, nullable=False, comment="名字")
    verify_code = db.Column(db.String(32), unique=True, comment="信箱驗證碼")
    email = db.Column(db.String(60), nullable=False, unique=True, comment="信箱")
    password = db.Column(db.String(60), nullable=False, comment="密碼")
    active_state = db.Column(db.Integer, default=0, comment="帳號狀態")
    set_password_code = db.Column(db.String(32), unique=True, comment="設定密碼驗證碼")
    role = db.Column(db.Integer, default=1, comment="帳號權限")

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.active_state}', '{self.role}')"


class VisitInfo(db.Model, UserMixin):
    __tablename__ = 'visit_info'
    id = db.Column(db.Integer, primary_key=True, comment="資料索引")
    name = db.Column(db.String(60), nullable=False, comment="名字")
    email = db.Column(db.String(60), nullable=False, unique=True, comment="信箱")

    def __repr__(self):
        return f"Visit('{self.name}', '{self.email}')"

