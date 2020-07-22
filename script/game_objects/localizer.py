import re

class Localizer:
    """Lookup and manage the English localization strings"""

    def __init__(self, loc_data):
        self.loc_data = loc_data

    def get(self, key):
        """Default is to return original string if we cannot translate it"""
        return self.get_or_default(key, key)
    
    def get_or_default(self, key, default):
        """Helper to return a different default value, most often None"""
        l = self._localize(key)
        if l is None:
            return default
        return l

    def get_with_log(self, key, msg):
        """Same as get() but log failures to console"""
        l = self._localize(key)
        if l is None:
            print("Localization key [{}][{}] not found: {}".format(self.as_key(key), repr(key), msg))
            return key
        return l

    def put_if_not_exist(self, key, value):
        """Add a value for a key if it does not already exist"""
        l = self._localize(key)
        if l is None:
            self.loc_data[key] = value

    def as_key(self, key):
        return key if type(key) is str else key.group(1)

    def _localize(self, key):
        """Private helper to do case insensitive lookups and $TERM$ substitution"""
        key = self.as_key(key)
        localized = next((value for dict_key, value in self.loc_data.items() if dict_key.lower() == key.lower()), None)
        # print(' ++ loc {} -> {}'.format(repr(key), repr(localized)))
        if localized is None:
            # No log message here, we are going to call a lot of trial lookups
            return localized
        if localized == '$' + key + '$':
            print(' ++ WARNING: INFINITE RECURSION STOPPED in Localizer::_localize: {} -> {}'.format(repr(key), repr(localized)))
            return localized
        while '$' in localized:
            replaced = re.sub(r'\$(\w+)\$', self._localize, localized)
            if replaced == localized:
                localized = re.sub(r'\$', '', localized)
                break
            localized = replaced
        return localized