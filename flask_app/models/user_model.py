from flask_app.config.mysqlconnection import connectToMySQL

class User:
    def __init__(self, data):
        self.id = data.get('id')
        self.email = data.get('email')
        self.password_hash = data.get('password_hash')
        self.account_level = data.get('account_level')

    @classmethod
    def get_user_by_id(cls, **data):
        query = "SELECT * FROM users WHERE id=%(id)s;"
        connection = connectToMySQL("terminal_archive")
        user = connection.query_db(query, data)
        connection.connection.close()
        if user:
            return cls(user[0])