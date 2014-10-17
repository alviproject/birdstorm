class ResourceContainer:
    """mixed in class"""
    def __init__(self, *args, **kwargs):
        self.resources = self.data.get('resources', {})

    def save(self, *args, **kwargs):
        self.data['resources'] = self.resources

    def add_resource(self, type, quantity):
        self.resources[type] = self.resources.get(type, 0) + quantity

    def remove_resource(self, type, quantity):
        if quantity == 0:
            return
        current = self.resources.get(type, 0)
        if current < quantity:
            raise RuntimeError("Not enought resources")
        if current == quantity:
            del self.resources[type]
            return
        self.resources[type] -= quantity
