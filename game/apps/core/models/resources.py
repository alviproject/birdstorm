class Resource:
    @classmethod
    @property
    def name(cls):
        return cls.__name__


class Coal(Resource):
    weight = 100


class IronOre(Resource):
    weight = 400