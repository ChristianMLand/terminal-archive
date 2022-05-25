from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import container_model, ssl_model 
from datetime import datetime, date, timedelta, timezone


class Availability:
    def __init__(self, data):
        self.id = data.get('id')
        self.terminal = data.get('name')
        self.container = data.get('size')
        self.ssl = data.get('ssls.name')
        self.first_available = data.get('first_available')
        self.last_available = data.get('last_available')
        self.type = data.get('type')

    @classmethod
    def retrieve_all(cls, form_data):
        data = {}
        query = '''
                SELECT 
                availabilities.id,
                availabilities.type,
                terminals.name, 
                ssls.name, 
                containers.size,
                MIN(created_at) AS "first_available", 
                MAX(created_at) AS "last_available"
                FROM (
                    SELECT 
                    availabilities.*,
                    @group_num := IF(
                        @prev_terminal_id != terminal_id OR @prev_ssl_id != ssl_id OR @prev_container_id != container_id OR @prev_type != type, 
                        @group_num + 1,
                        @group_num
                    ) AS gn,
                    @prev_terminal_id := terminal_id,
                    @prev_container_id := container_id,
                    @prev_ssl_id := ssl_id,
                    @prev_type := type
                    FROM availabilities,
                    (SELECT @group_num := 0, @prev_terminal_id := NULL, @prev_container_id := NULL, @prev_ssl_id := NULL, @prev_type := NULL) var_init_subquery
                    ORDER BY terminal_id, ssl_id, container_id, created_at
                ) availabilities
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
        if data.get('type','None') in 'pick,drop':
            data['type'] = f"%{data['type']}%"
            query += 'AND TYPE LIKE %(type)s '
        wheres = ""
        for key in data:
            if key not in ['type','start_date','end_date']:
                wheres += f"AND {key} in (%({key})s) "
        query += wheres
        query += "GROUP BY gn, terminal_id, ssl_id, container_id, type ORDER BY created_at DESC;"
        results = connectToMySQL("terminal_archive").query_db(query, data)
        if results:
            return [cls(row) for row in results]
        return results

    @staticmethod
    def create(terminal, data):
        ssls = ssl_model.SSL.retrieve_all()
        containers = container_model.Container.retrieve_all()
        query = 'INSERT INTO availabilities (terminal_id, ssl_id, container_id, type) VALUES'
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
                query += f" ({availability['terminal_id']}, {availability['ssl_id']}, {availability['container_id']}, '{availability['types']}'),"
        query = query[:-1] + ";"
        return connectToMySQL("terminal_archive").query_db(query)
    
    @property
    def json(self):
        return {
            "id" : self.id,
            "terminal" : self.terminal,
            "container" : self.container,
            "ssl" : self.ssl,
            "first_available" : self.first_available,
            "last_available" : self.last_available,
            "type" : self.type
        }
