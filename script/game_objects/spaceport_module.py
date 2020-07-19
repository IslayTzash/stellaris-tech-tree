class SpaceportModule:
    def __init__(self, spaceport_module, localizer):
        self.key = list(spaceport_module.keys())[0]
        self.name = localizer.get_or_default('sm_' + self.key, self.key)
        module_data = spaceport_module[self.key]
        self.prerequisites = self._prerequisites(module_data)

    def _prerequisites(self, module_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in module_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
