import abc
from game.apps.core.models.components.base import Component


class Engine(Component):
    @staticmethod
    def create(data):
        if type not in data or data['type'] == "JetEngine":
            return JetEngine(data.get('mark', 1))

    @abc.abstractmethod
    def output(self):
        raise NotImplementedError

    @abc.abstractmethod
    def range(self):
        raise NotImplementedError

    def parameters(self):
        return {
            "range": self.range(),
            "output": self.output(),
        }

    @classmethod
    def kind(cls):
        return "Engine"


class JetEngine(Engine):
    def output(self):
        return int((1.2**self.mark) * 10)

    def range(self):
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
                'ComponentStructures': n
            }
        }