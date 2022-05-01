class Availability:
    def __init__(self, data):
        self.id = data.get('id')
        self.partnership_id = data.get('partnership_id')
        self.container_id = data.get('container_id')
        self.created_at = data.get('created_at')
        self.type = data.get('type')

    @staticmethod
    def create(data):
        pass

    @classmethod
    def retrieve(cls):
        pass