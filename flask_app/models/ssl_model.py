from flask_app.config.mysqlconnection import connectToMySQL

class SSL:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
    
    @classmethod
    def retrieve_all(cls):
        query = "SELECT * FROM ssls;"
        results = connectToMySQL("terminal_archive").query_db(query)
        return [cls(row) for row in results]