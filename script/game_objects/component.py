from .game_object import GameObject

class Component(GameObject):
    def __init__(self, data, localizer):
        # self.key will be set prior to invoking _name()
        data = list(data.values())[0]
        self.key = self._key(data)
        self.name = self._name(localizer)
        self.prerequisites = self._prerequisites(data)

    def _key(self, component_data):        
        return next(iter(
            subkey for subkey in component_data if list(subkey.keys())[0] == 'key'
        ))['key']
