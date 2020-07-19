import re

class BuildablePop:
    def __init__(self, buildable_pop, localizer):
        self.key = list(buildable_pop.keys())[0]
        self.name = localizer.get(self.key)
        buildable_pop_data = buildable_pop[self.key]
        self.prerequisites = self._prerequisites(buildable_pop_data)

    def _prerequisites(self, buildable_pop_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in buildable_pop_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
