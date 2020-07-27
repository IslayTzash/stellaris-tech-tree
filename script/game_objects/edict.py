from .game_object import GameObject

class Edict(GameObject):
    def _name(self, localizer):
        return localizer.get_or_default('edict_' + self.key, self.key)
