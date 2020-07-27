from .game_object import GameObject

class SpaceportModule(GameObject):
    def _name(self, localizer):
        return localizer.get_or_default('sm_' + self.key, self.key)
