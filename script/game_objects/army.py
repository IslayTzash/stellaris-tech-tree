class Army:
    def __init__(self, army, localizer):
        self.key = list(army.keys())[0]
        self.name = localizer.get(self.key)
        army_data = army[self.key]
        self.prerequisites = self._prerequisites(army_data)

    def _prerequisites(self, army_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in army_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
