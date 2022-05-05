from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import bcrypt, DB
from flask import flash
from flask_app.utility.utils import generate_password
from flask_app.models.base_model import Model

class User(Model):
    table="users"

    def __init__(self, data):
        self.id = data.get('id')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.account_level = data.get('account_level')

    @staticmethod
    def create(form_data):
        password = generate_password()
        data = {
            "email" : form_data.get('email'),
            "hash" :  bcrypt.generate_password_hash(password)
        }
        query = '''
                INSERT INTO users
                (email, password_hash)
                VALUES
                (%(email)s, %(hash)s);
                '''
        user_id = connectToMySQL(DB).query_db(query, data)
        return user_id, password

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