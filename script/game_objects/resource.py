class Resource:
    def __init__(self, resource, localizer):
        self.key = list(resource.keys())[0]
        self.name = localizer.get(self.key)
        resource_data = resource[self.key]
        self.prerequisites = self._prerequisites(resource_data)

    def _prerequisites(self, resource_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in resource_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
