class GameObject:
    def __init__(self, yaml, localizer):
        # self.key will be set prior to invoking _name()
        self.key = self._key(yaml)
        self.name = self._name(localizer)
        self.prerequisites = self._prerequisites(yaml[self.key])

    def _name(self, localizer):
        return localizer.get(self.key)

    def _key(self, yaml):
        return list(yaml.keys())[0]

    def _prerequisites(self, data):
        try:
            prerequisites = next(iter(
                subkey for subkey in data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []
        return prerequisites