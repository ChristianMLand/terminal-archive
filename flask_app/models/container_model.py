from flask_app.models.base_model import Model

class Container(Model):
    table="containers"

    def __init__(self, data):
        self.id = data.get('id')
        self.size = data.get('size')

    @property
    def json(self):
        return {
            "id" : self.id,
            "size" : self.size
        }