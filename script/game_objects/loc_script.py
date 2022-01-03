from .game_object import GameObject

class LocScript(GameObject):
    def __init__(self, data, localizer):
        self.name = None
        self.value = None
        for v in data.values():
            self.name = self._valueOrDefault(v, 'name', None)
            self.value = self._valueOrDefault(v, 'default', None)
            #if name and value:
            #    print(name + ' = ' + value)