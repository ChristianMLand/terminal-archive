from flask_app.config.mysqlconnection import connectToMySQL

class SSL:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')

    @staticmethod
    def create(data):
        query = '''
                INSERT INTO ssls (name)
                VALUES (%(name)s);
                '''
        return connectToMySQL(query, data)

    @classmethod
    def retrieve(cls, data):
        query = '''
                SELECT * FROM ssls;
                '''
        return connectToMySQL(query, data)


