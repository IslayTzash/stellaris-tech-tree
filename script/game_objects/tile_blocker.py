class TileBlocker:
    def __init__(self, tile_blocker, localizer):
        self.key = list(tile_blocker.keys())[0]
        self.name = localizer.get(self.key)
        blocker_data = tile_blocker[self.key]
        self.prerequisites = self._prerequisites(blocker_data)

    def _prerequisites(self, blocker_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in blocker_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
