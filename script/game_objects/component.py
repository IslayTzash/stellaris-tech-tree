from .game_object import GameObject

class Component(GameObject):
    def __init__(self, yaml, localizer):
        # self.key will be set prior to invoking _name()
        yaml = list(yaml.values())[0]
        self.key = self._key(yaml)
        self.name = self._name(localizer)
        self.prerequisites = self._prerequisites(yaml)

    def _key(self, component_data):        
        return next(iter(
            subkey for subkey in component_data if list(subkey.keys())[0] == 'key'
        ))['key']
