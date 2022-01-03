from .game_object import GameObject

class Policy(GameObject):
    def __init__(self, policy, localizer):
        self.key = list(policy.keys())[0]
        self.name = localizer.get_or_default('policy_' + self.key, self.key)
        self.options = self._options(policy[self.key], localizer)

    def _options(self, policy_data, localizer):
        return [Option(entry['option'], localizer)
                for entry in policy_data
                if list(entry.keys())[0] == 'option']


class Option(GameObject):
    def __init__(self, option_data, localizer):
        self.name = self._name(option_data, localizer)
        self.prerequisites = self._prerequisites(option_data)

    def _name(self, option_data, localizer):        
        unlocalized = self._valueOrDefault(option_data, 'name', None)
        return localizer.get(unlocalized)
