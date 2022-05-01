from types import ClassMethodDescriptorType


class Container:
    def __init__(self, data):
        self.id = data.get('id')
        self.size = data.get('size')

    @classmethod
    def get_one(cls, data):
        pass

    @classmethod
    def get_all(cls, data):
        pass