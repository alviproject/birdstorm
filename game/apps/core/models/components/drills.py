import abc
from game.apps.core.models.components.base import Component


class Drill(Component):
    @staticmethod
    def create(data):
        if type not in data or data['type'] == "SteelDrill":
            return SteelDrill(data.get('mark', 1))

    @abc.abstractmethod
    def deepness(self):
        raise NotImplementedError

    @abc.abstractmethod
    def speed(self):
        raise NotImplementedError

    def parameters(self):
        return {
            "deepness": self.deepness(),
            "speed": self.speed(),
        }

    @classmethod
    def kind(cls):
        return "Drill"


class SteelDrill(Drill):
    def deepness(self):
        return int((1.2**self.mark) * 10)

    def speed(self):
        return int((1.2**self.mark) * 0.2)

    def process_cost(self):
        if self.mark == 1:
            n = 10
            time = 10
        else:
            n = int(1.3**self.mark)
            time = int(1.3**self.mark * 5)
        return {
            'time': time,
            'requirements': {
                'ComponentStructures': n,
                'Steel': 10,
            }
        }