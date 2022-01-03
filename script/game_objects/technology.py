from deep_parsers.feature_unlocks import FeatureUnlocks
from deep_parsers.weight_modifiers import WeightModifiers
from json import JSONEncoder
from .game_object import GameObject

class Technology(GameObject):
    def __init__(self, tech, icon_remaps, armies, army_attachments, buildable_pops,
                 buildings, components, edicts, policies, resources,
                 spaceport_modules, tile_blockers, localizer,
                 start_with_tier_zero=True):
        self.key = list(tech.keys())[0]
        self._localizer = localizer
        self.name = localizer.get(self.key)

        tech_data = tech[self.key]

        self.description = self._description()
        self.area = next(iter(key for key in tech_data
                              if list(key.keys())[0] == 'area'))['area']
        self.category = localizer.get(
            next(iter(key for key in tech_data
                      if list(key.keys())[0] == 'category'))['category'][0]
        )

        self.tier = next(
            iter(key for key in tech_data if list(key.keys())[0] == 'tier')
        )['tier']

        icon = self._valueOrDefault(tech_data, 'icon', None)
        if icon:
            self.icon = icon
            if icon in icon_remaps:
                self.icon = icon_remaps[icon]
        elif self.key in icon_remaps:
            self.icon  = icon_remaps[self.key]

        self.cost = self._valueOrDefault(tech_data, 'cost', '0')
        self.base_weight = self._valueOrDefault(tech_data, 'weight', 0)
        self.base_factor = self._base_factor(tech_data)
        self.weight_modifiers = self._weight_modifiers(tech_data)
        self.prerequisites = self._prerequisites(tech_data)
        self.is_start_tech = self._is_start_tech(tech_data,
                                                 start_with_tier_zero)
        self.is_dangerous = self._boolFromYes(tech_data, 'is_dangerous')
        self.is_rare = self._boolFromYes(tech_data, 'is_rare')
        self.dlc = self._dlc(tech_data)

        unlock_parser = FeatureUnlocks(armies, army_attachments,
                                       buildable_pops, buildings, components,
                                       edicts, policies, resources,
                                       spaceport_modules, tile_blockers,
                                       localizer)
        self.feature_unlocks = unlock_parser.parse(self.key, tech_data)

    def _is_start_tech(self, tech_data, start_with_tier_zero):
        is_start_tech = self._valueOrDefault(tech_data, 'start_tech', None)
        if is_start_tech is None:
            is_start_tech = True if self.tier == 0 and start_with_tier_zero else False
        return is_start_tech

    def _description(self):
        try:
            description = self._localizer.get(self.key + '_desc')
            self.description = (self._localizer.get(description.replace('$', ''))
                                if description.startswith('$')
                                else description)
        except KeyError:
            description = None

        return description

    def _prerequisites(self, tech_data):
        if self.key in ['tech_biolab_1', 'tech_physics_lab_1',
                        'tech_engineering_lab_1']:
            return ['tech_basic_science_lab_1']
        else:
            return super()._prerequisites(tech_data)

    def _base_factor(self, tech_data):
        try:
            factor = next(
                iter(key for key in tech_data
                     if list(key.keys())[0] == 'weight_modifier')
            )['weight_modifier'][0]['factor']
        except (StopIteration, KeyError, IndexError):
            factor = 1.0

        return float(factor)

    def _weight_modifiers(self, tech_data):
        wm = WeightModifiers(self._localizer)
        unparsed_modifiers = self._valueOrDefault(tech_data, 'weight_modifier', [])
        return [wm.parse(modifier['modifier'])
                for modifier in unparsed_modifiers
                if list(modifier.keys()) == ['modifier']]

    def _dlc(self, tech_data):
        try:
            dlc = next(iter(
                key for key in tech_data if list(key.keys())[0] == 'potential'
            ))['potential']
            for d in dlc:
                if 'host_has_dlc' in d:
                    return [ d['host_has_dlc'] ]
        except StopIteration:
            pass    
        return []

class TechnologyJSONEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Technology):
            encoder = {key: getattr(object, key) for key
                       in list(object.__dict__.keys())
                       if not key.startswith('_')}
        else:
            encoder = JSONEncoder.default(self, object)

        return encoder
