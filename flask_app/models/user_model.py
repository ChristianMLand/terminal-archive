from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import bcrypt
from flask import flash
from flask_app.utility.utils import generate_password

class User:
    def __init__(self, data):
        self.id = data.get('id')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.account_level = data.get('account_level')
#-----------------------Create----------------------------------#
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
        user_id = connectToMySQL("terminal_archive").query_db(query, data)
        return user_id, password
#------------------------Retrieve--------------------------------#
    @classmethod
    def retrieve_one(cls, **data):
        query = "SELECT * FROM users WHERE id=%(id)s;"
        results = connectToMySQL("terminal_archive").query_db(query, data)
        if results:
            return cls(results[0])
    
    @classmethod
    def retrieve_by_email(cls, **data):#TODO combine with retrieve one
        query = "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL("terminal_archive").query_db(query, data)
        if results:
            return cls(results[0])
#------------------------Update----------------------------------#
    @staticmethod
    def update(data):#TODO make dynamic to handle both account level and password
        query = '''
                UPDATE users
                SET account_level = %(account_level)s
                WHERE users.id = %(id)s;
                '''
        return connectToMySQL("terminal_archive").query_db(query, data)
#--------------------------Delete---------------------------------#
    @staticmethod
    def delete(data):
        query = '''
                DELETE FROM users
                WHERE id = %(id)s;
                '''
        return connectToMySQL("terminal_archive").query_db(query, data)
#-------------------------Validatate-------------------------------#
    @staticmethod
    def validate(data):
        user = User.retrieve_by_email(email=data['email'])
        errors = {}
        if not user:
            errors['email'] = "Email has not been granted access"
        elif not bcrypt.check_password_hash(user.password_hash, data['password']):
            errors['password'] = "Invalid Password"
        for k,v in errors.items():
            flash(v,k)
        return len(errors) == 0
#------------------------------------------------------------------#