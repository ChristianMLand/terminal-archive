import requests
from bs4 import BeautifulSoup
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.parser_model import TerminalParser

class Terminal:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.auth_email = data.get('auth_email')
        self.auth_password = data.get('auth_password')
        self.auth_required = data.get('auth_required')
        self.auth_url = data.get('auth_url')
        self.data_url = data.get('data_url')

    def parse(self):
        if self.auth_required:
            with requests.session() as s:
                s.post(self.auth_url, data={"j_username" : self.auth_email, "j_password" : self.auth_password})
                r = s.get(self.data_url)
        else:
            r = requests.get(self.data_url)
        soup = BeautifulSoup(r.content, "html.parser")
        return TerminalParser.get_parser(self.name).parse(soup)

    @classmethod
    def retrieve_all(cls):
        query = "SELECT * FROM terminals;"
        results = connectToMySQL("terminal_archive").query_db(query)
        return [cls(row) for row in results]

    @classmethod
    def retrieve_one(cls, **data):
        query = "SELECT * FROM terminals WHERE id=%(id)s;"
        results = connectToMySQL("terminal_archive").query_db(query, data)
        if results:
            return cls(results[0])

    @staticmethod
    def update(data):
        query = '''
                UPDATE terminals 
                SET auth_email=%(auth_email)s, auth_password=%(auth_password)s
                WHERE id=%(terminal_id)s;
                '''
        return connectToMySQL("terminal_archive").query_db(query, data)
    
    @property
    def json(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "auth_email" : self.auth_email,
            "auth_password" : self.auth_password,
            "auth_required" : self.auth_required,
            "auth_url" : self.auth_url,
            "data_url" : self.data_url
        }