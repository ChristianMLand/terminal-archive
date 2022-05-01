class Terminal:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.auth_email = data.get('auth_email')
        self.auth_password = data.get('auth_password')
        self.auth_url = data.get('auth_url')
        self.auth_required = data.get('auth_required')
        self.data_url = data.get('data_url')

    @staticmethod
    def update(data):
        pass

    @classmethod
    def get_all(cls, data):
        pass