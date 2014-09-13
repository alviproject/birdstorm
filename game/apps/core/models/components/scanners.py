import abc
from game.apps.core.models.components.base import Component


class Scanner(Component):
    @staticmethod
    def create(data):
        if type not in data or data['type'] == "BaseScanner":
            return BaseScanner(data.get('mark', 1))

    @abc.abstractmethod
    def deepness(self):
        raise NotImplementedError

    def parameters(self):
        return {
            "deepness": self.deepness(),
        }

    @classmethod
    def kind(cls):
        return "Scanner"


class BaseScanner(Scanner):
    def deepness(self):
        return int((1.2**self.mark) * 10)

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