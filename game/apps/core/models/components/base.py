class Component:
    def __init__(self, mark):
        self.mark = mark
        self.type = self.__class__.__name__

    def process(self):
        result = self.process_cost()
        result.update({
            "parameters": self.parameters(),
            "mark": self.mark,
            "kind": self.kind(),
        })
        return result

    def serialize(self):
        return {
            "mark": self.mark,
            "type": self.type,
        }