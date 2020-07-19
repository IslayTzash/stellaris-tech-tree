class ArmyAttachment:
    def __init__(self, attachment, localizer):
        self.key = list(attachment.keys())[0]
        self.name = localizer.get_or_default('army_attachment_' + self.key, self.key)
        attachment_data = attachment[self.key]
        self.prerequisites = self._prerequisites(attachment_data)

    def _prerequisites(self, attachment_data):
        try:
            prerequisites = next(iter(
                subkey for subkey in attachment_data
                if list(subkey.keys())[0] == 'prerequisites'
            ))['prerequisites']
        except (StopIteration):
            prerequisites = []

        return prerequisites
