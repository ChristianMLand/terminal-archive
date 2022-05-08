from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import bcrypt, DB
from flask import flash, session
from flask_app.utility.utils import generate_password
from flask_app.models.base_model import Model

class User(Model):
    table="users"

    def __init__(self, data):
        self.id = data.get('id')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.account_level = data.get('account_level')

    @classmethod
    def create(cls, **form_data):
        if len(form_data.get("email","")) < 1:
            return False
        password = generate_password()
        data = {
            "email" : form_data.get('email'),
            "password_hash" :  bcrypt.generate_password_hash(password)
        }
        user_id = super().create(**data)
        if user_id:
            return {
                "email" : data['email'],
                "password" : password,
                "id" : user_id
            }
        return False

    @classmethod
    def update(cls, **form_data):
        logged_user = User.retrieve_one(id=session['user_id'])
        if form_data.get('new_password'):
            if len(form_data['new_password']) < 8:
                return False
            data = {"id" : logged_user.id}
            if bcrypt.check_password_hash(logged_user.password_hash, form_data.get('old_password', '')):
                data['password_hash'] = bcrypt.generate_password_hash(form_data['new_password'])
                return super().update(**data)
        if form_data.get('account_level', 3) < logged_user.account_level:
            print(logged_user.id, form_data)
            if logged_user.id != form_data.get("id", logged_user.id):
                return super().update(**form_data)
            return False
        return False

    @classmethod
    def delete(cls, **form_data):
        logged_user = User.retrieve_one(id=session['user_id'])
        to_delete = User.retrieve_one(id=form_data.get("id"))
        if logged_user.account_level <= to_delete.account_level:
            return False
        return super().delete(**form_data)

    @staticmethod
    def validate(data):
        user = User.retrieve_one(email=data['email'])
        errors = {}
        if not user:
            errors['email'] = "Email has not been granted access"
        elif not bcrypt.check_password_hash(user.password_hash, data['password']):
            errors['password'] = "Invalid Password"
        for k,v in errors.items():
            flash(v,k)
        return len(errors) == 0