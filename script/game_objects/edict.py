class Edict:
    def __init__(self, edict_data, localizer):
        name = self._name(edict_data)
        self.name = localizer.get_or_default('edict_' + name, name)
        self.prerequisites = self._prerequisites(edict_data[name])

    def _name(self, edict_data):
        return next(iter(edict_data))

    def _prerequisites(self, edict_list):
        for e in edict_list:
            if 'prerequisites' in e:
                return e['prerequisites']
        return []
