from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import container_model, ssl_model, terminal_model
from datetime import datetime, date

class Availability:
    def __init__(self, data):
        self.id = data.get('id')
        self.terminal = data.get('name')
        self.container = data.get('size')
        self.ssl = data.get('ssls.name')
        self.created_at = data.get('created_at')
        self.type = data.get('type')

    @classmethod
    def retrieve_all(cls, form_data):
        data = {}

        query = '''
                SELECT 
                availabilities.id, 
                terminals.name, ssls.name, 
                containers.size, 
                availabilities.created_at, 
                availabilities.type
                FROM availabilities
                JOIN terminals ON terminals.id = terminal_id
                JOIN ssls ON ssls.id = ssl_id
                JOIN containers ON containers.id = container_id
                WHERE
                created_at BETWEEN %(start_date)s AND %(end_date)s
                '''
        data['start_date'] = datetime.strptime(form_data['start_date'], '%Y-%m-%dT%H:%M') if form_data['start_date'] else date.today()
        data['end_date'] = datetime.strptime(form_data['end_date'], '%Y-%m-%dT%H:%M') if form_data['end_date'] else datetime.now()
        for key in form_data:
            if key not in data:
                data[key] = form_data.getlist(key)
        for key in data:
            if key in ['type','terminal_id','ssl_id','container_id']:
                data[key] = "','".join(data[key])
        if data.get('type'):
            query += 'AND TYPE LIKE "%%(type)s%"'
        query += "AND " + "AND ".join(f'{key} in (%({key})s) ' for key in data if key not in ['type','start_date','end_date'])
        query += "ORDER BY created_at DESC;"
        print(query,data)
        results = connectToMySQL("terminal_archive").query_db(query, data)
        return [cls(row) for row in results]

    @staticmethod
    def create(terminal, data):
        ssls = ssl_model.SSL.retrieve_all()
        containers = container_model.Container.retrieve_all()

        query = '''
                INSERT INTO availabilities
                (terminal_id, ssl_id, container_id, type)
                VALUES
                (%(terminal_id)s, %(ssl_id)s, %(container_id)s, %(types)s);
                '''

        for line in data:
            availability = {"terminal_id" : terminal.id}
            for ssl in ssls:
                if line == ssl.name:
                    availability['ssl_id'] = ssl.id
            for cont in data[line]:
                for container in containers:
                    if cont in container.size:
                        availability['container_id'] = container.id
                        availability['types'] = ','.join(data[line][cont])
                connectToMySQL("terminal_archive").query_db(query, availability)
    
    @property
    def json(self):
        return {
            "id" : self.id,
            "terminal" : self.terminal,
            "container" : self.container,
            "ssl" : self.ssl,
            "created_at" : self.created_at,
            "type" : self.type
        }
