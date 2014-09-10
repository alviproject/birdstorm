class Component:
    def __init__(self, mark):
        self.mark = mark
        self.type = self.__class__.__name__

    def process(self):
        result = self.process_cost()
        result.update({
            "parameters": self.parameters()
        })
        return result