class Edict:
    def __init__(self, edict_data, loc_data):
        name = self._name(edict_data)
        self.name = loc_data.get('edict_' + name, name)
        self.prerequisites = self._prerequisites(edict_data[name])

    def _name(self, edict_data):
        return next(iter(edict_data))

    def _prerequisites(self, edict_list):
        for e in edict_list:
            if 'prerequisites' in e:
                return e['prerequisites']
        return []
