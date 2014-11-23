class ResourceContainer:
    """mixed in class"""
    @property
    def resources(self):
        return self.data.setdefault("resources", {})

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
