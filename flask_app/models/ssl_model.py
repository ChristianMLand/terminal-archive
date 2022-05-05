from flask_app.models.base_model import Model

class SSL(Model):
    table = "ssls"

    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')

    @property
    def json(self):
        return {
            "id" : self.id,
            "name" : self.name
        }