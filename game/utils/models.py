class ResourceContainer:
    """mixed in class"""
    @property
    def resources(self):
        return self.data.get('resources', {})

    def add_resource(self, type, quantity):
        resources = self.data.setdefault('resources', {})
        resources[type] = resources.get(type, 0) + quantity

    def remove_resource(self, type, quantity):
        if quantity == 0:
            return
        resources = self.data.setdefault('resources', {})
        current = resources.get(type, 0)
        if current < quantity:
            raise RuntimeError("Not enought resources")
        if current == quantity:
            del resources[type]
            return
        resources[type] -= quantity
