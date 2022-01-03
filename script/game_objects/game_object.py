class GameObject:
    def __init__(self, data, localizer):
        # self.key will be set prior to invoking _name()
        self.key = self._key(data)
        self.name = self._name(localizer)
        self.prerequisites = self._prerequisites(data[self.key])

    def _name(self, localizer):
        return localizer.get(self.key)

    def _key(self, data):
        return list(data.keys())[0]

    def _prerequisites(self, data):
        return self._valueOrDefault(data, 'prerequisites', [])

    def _valueOrDefault(self, data, name, default):
        try:
            val = next(iter(key for key
                               in data
                               if list(key.keys())[0] == name))[name]
        except StopIteration:
            val = default
        return val

    def _boolFromYes(self, data, name, default = False):
        try:
            yes_no = next(iter(key for key in data if list(key.keys())[0] == name))[name]
            yes_no = True if yes_no.lower() == 'yes' else False
        except StopIteration:
            yes_no = default
        return yes_no