from abc import ABC,abstractstaticmethod
import requests
from bs4 import BeautifulSoup
import json
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.container_model import Container
from flask_app.models.ssl_model import SSL

container_size_aliases = {
    "20" : ["20DR"],
    "Reefer" : ["20RFR", "40RFR"],
    "HT/OT" : ["Special"],
    "FR" : ["Special"],
    "OT" : ["Special"],
    "HT" : ["Special"],
}

#TODO write helper methods for getting container sizes and ssl_names in abc class
#TODO write helper method for getting availability type and storing in info_dict

class TerminalParser(ABC):
    @abstractstaticmethod
    def parse() -> dict:
        ...

    def get_parser(terminal_name) -> 'TerminalParser':
        terminals = {
            "t18" : T18Parser,
            "t30" : T30Parser,
            "t5" : T5Parser,
            "wut" : WUTParser,
            "husky" : HuskyParser
        }
        return terminals[terminal_name]()

class T18Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[1]
        rows = table.find_all("tr")[1:14]
        container_sizes = [td.getText().split(" ")[0].replace("'","").strip() for td in table.tr.find_all("td")[1:]]
        ssl_names = [tr.td.getText().replace("YES","").strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all('td')[1:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        for line in ssl_names[i].split('/'):
                            data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class T30Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        #TODO build this 
        pass

class T5Parser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        tables = soup.find_all("table")
        container_sizes = [td.getText().strip() for td in tables[1].tr.find_all("td")[1:]]
        ssl_names = []
        for x, table in enumerate(tables[1:]):
            rows = table.find_all("tr")[1:]
            for tr in rows:
                line = tr.td.getText().strip()
                if line not in ssl_names:
                    ssl_names.append(line)
            for i, tr in enumerate(rows):
                info_dict = {}
                for j, td in enumerate(tr.find_all("td")[1:]):
                    container = container_sizes[j]
                    line = ssl_names[i]
                    if td.getText().strip() == "OPEN":
                        availability_type = "Pick" if x else "Drop"
                        if line not in data:
                            data[line] = info_dict
                        else:
                            info_dict = data[line]
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class WUTParser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[0].tbody
        rows = table.find_all("tr")[1:]
        container_sizes = [td.getText().replace("’ ","").replace("Pick Up", "").replace("Drop", "").strip() for td in table.tr.find_all("td")[1:]]
        ssl_names = [tr.td.getText().strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all("td")[1:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        line = ssl_names[i]
                        data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class HuskyParser(TerminalParser):
    @staticmethod
    def parse(soup):
        data = {}
        table = soup.find_all("table")[2]
        rows = table.tbody.find_all("tr")
        container_sizes = [th.getText().replace("' ","").replace("Drop","").replace("Pick","").strip() for th in table.thead.tr.find_all("th")[2:]]
        ssl_names = [tr.find_all("td")[1].getText().strip() for tr in rows]
        for i, tr in enumerate(rows):
            info_dict = {}
            for j, td in enumerate(tr.find_all("td")[2:]):
                containers = [container_sizes[j]]
                if containers[0] in container_size_aliases:
                    containers = container_size_aliases[containers[0]]
                for container in containers:
                    if td.getText().strip() == "YES":
                        availability_type = "Pick" if j % 2 else "Drop"
                        line = ssl_names[i]
                        data[line] = info_dict
                        if container in info_dict:
                            info_dict[container].append(availability_type)
                        else:
                            info_dict[container] = [availability_type]
        return data

class Terminal:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.auth_email = data.get('auth_email')
        self.auth_password = data.get('auth_password')
        self.auth_required = data.get('auth_required')
        self.auth_url = data.get('auth_url')
        self.data_url = data.get('data_url')
        self.parser = TerminalParser.get_parser(self.name)

    def parse(self):
        if self.auth_required:
            with requests.session() as s:
                s.post(self.auth_url, data={"j_username" : self.auth_email, "j_password" : self.auth_password})
                r = s.get(self.data_url)
        else:
            r = requests.get(self.data_url)
        soup = BeautifulSoup(r.content, "html.parser")
        return self.parser.parse(soup)

    def update_db(self, data):
        ssls = SSL.retrieve_all()
        containers = Container.retrieve_all()

        query = '''
                INSERT INTO availabilities
                (terminal_id, ssl_id, container_id, type)
                VALUES
                (%(terminal_id)s, %(ssl_id)s, %(container_id)s, %(types)s);
                '''

        for line in data:
            availability = {"terminal_id" : self.id}
            for ssl in ssls:
                if line == ssl.name:
                    availability['ssl_id'] = ssl.id
            for cont in data[line]:
                for container in containers:
                    if cont in container.size:
                        availability['container_id'] = container.id
                        availability['types'] = ','.join(data[line][cont])
                connectToMySQL("terminal_archive").query_db(query, availability)

    @classmethod
    def retrieve_all(cls):
        query = "SELECT * FROM terminals;"
        results = connectToMySQL("terminal_archive").query_db(query)
        return [cls(row) for row in results]

    @classmethod
    def retrieve_one(cls, **data):
        query = "SELECT * FROM terminals WHERE id=%(id)s;"
        results = connectToMySQL("terminal_archive").query_db(query)
        if results:
            return cls(results[0])