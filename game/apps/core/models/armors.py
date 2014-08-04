class Armor:
    def __init__(self):
        self._defense_left = self.defense()

    @classmethod
    def defense(cls):
        return 100

    @property
    def defense_left(self):
        return self._defense_left

    @defense_left.setter
    def defense_left(self, value):
        self._defense_left = value