from flask_app.config.mysqlconnection import connectToMySQL

class Container:
    def __init__(self, data):
        self.id = data.get('id')
        self.size = data.get('size')
    
    @classmethod
    def retrieve_all(cls):
        query = "SELECT * FROM containers;"
        results = connectToMySQL("terminal_archive").query_db(query)
        return [cls(row) for row in results]