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

    def put_if_not_exist(self, key, value):
        """Add a value for a key if it does not already exist"""
        l = self._localize(key)
        if l is None:
            self.loc_data[key] = value

    def _localize(self, key):
        """Private helper to do case insensitive lookups and $TERM$ substitution"""
        # Watch for keys with differing case, but we aren't careful with case when building MOD_ keys
        # ../localisation/english/megacorp_l_english.yml: empire_size:0 "$EMPIRE_SIZE$"
        # ../localisation/english/megacorp_l_english.yml: EMPIRE_SIZE:1 "Empire Sprawl"
        if key in self.loc_data:
            localized = self.loc_data[key]
        else:
            localized = next((value for dict_key, value in self.loc_data.items() if dict_key.lower() == key.lower()), None)
        if localized is None:
            # No log message here, we are going to call a lot of trial lookups
            return localized
        if localized == '$' + key + '$':
            print(' ++ WARNING: INFINITE RECURSION STOPPED in Localizer::_localize: {} -> {}'.format(repr(key), repr(localized)))
            return localized
        while '$' in localized:            
            replaced = re.sub(r'\$(\w+)\$', lambda x: self._localize(x.group(1)), localized)
            if replaced == localized:
                localized = re.sub(r'\$', '', localized)
                break
            localized = replaced
        return localized