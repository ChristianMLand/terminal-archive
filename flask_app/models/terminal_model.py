import requests
from bs4 import BeautifulSoup
from flask_app.models.parser_model import TerminalParser
from flask_app.models.base_model import Model

class Terminal(Model):
    table="terminals"

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
                s.post(self.auth_url, data={
                    "j_username" : self.auth_email, 
                    "j_password" : self.auth_password
                })
                r = s.get(self.data_url)
        else:
            r = requests.get(self.data_url)
        soup = BeautifulSoup(r.content, "html.parser")
        return TerminalParser.get_parser(self.name).parse(soup)

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