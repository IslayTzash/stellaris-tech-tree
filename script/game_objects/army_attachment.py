from .game_object import GameObject

class ArmyAttachment(GameObject):
    def _name(self, localizer):
        return localizer.get_or_default('army_attachment_' + self.key, self.key)
