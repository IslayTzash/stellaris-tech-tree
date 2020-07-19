class Building:
    def __init__(self, building, localizer):
        self.key = list(building.keys())[0]
        self.name = localizer.get(self.key)

        building_data = building[self.key]
        self.prerequisites = self._prerequisites(building_data)

    def _prerequisites(self, building_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in building_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
