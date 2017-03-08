# -*- coding: utf-8 -*-

from pprint import pprint
import re

# Modifiers gained as a result of completing research
class FeatureUnlockParser:
    def __init__(self, loc_data):
        self.loc_data = loc_data

    def parse(self, tech):
        return self.modifiers(tech) + self.unlocks(tech)

    def modifiers(self, tech):
        tech_key = tech.keys()[0]

        def localize(modifier):
            key = modifier.keys()[0]
            value = '{:+.0%}'.format(modifier[key]) if modifier[key] < 1 \
                    else '{:+d}'.format(modifier[key])
            loc_data = self.loc_data

            if key == 'all_technology_research_speed':
                key = 'MOD_COUNTRY_ALL_TECH_RESEARCH_SPEED'
            elif key == 'science_ship_survey_speed':
                key = 'MOD_SHIP_SCIENCE_SURVEY_SPEED'

            relocalize = lambda match: loc_data[match.group(1)]

            try:
                localized = {loc_data[key]: value}
            except KeyError:
                prefix = 'MOD_'
                alt_key = (prefix + key).upper()
                try:
                    localized_key = loc_data[alt_key]
                    while '$' in localized_key:
                        localized_key = re.sub(r'\$(\w+)\$',
                                               relocalize,
                                               localized_key)
                    localized = {localized_key: value}

                except KeyError:
                    prefix = 'MOD_COUNTRY_'
                    alt_key = (prefix + key).upper()
                    try:
                        localized = {loc_data[alt_key]: value}
                    except KeyError:
                        prefix = 'MOD_POP_'
                        alt_key = (prefix + key).upper()
                        try:
                            localized = {loc_data[alt_key]: value}
                        except KeyError:
                            prefix = 'MOD_PLANET_'
                            alt_key = (prefix + key).upper()
                            try:
                                localized = {loc_data[alt_key]: value}
                            except KeyError:
                                # Give up.
                                localized = {alt_key: value}



            return '{}: {}'.format(localized.keys()[0], localized.values()[0])

        try:
            acquired_modifiers = [localize(modifier) for modifier in next(iter(
                attribute for attribute in tech[tech_key]
                if attribute.keys()[0] == 'modifier'
            ))['modifier']]
        except (StopIteration):
            acquired_modifiers = []

        return acquired_modifiers


    def unlocks(self, tech):
        tech_key = tech.keys()[0]
        loc_data = self.loc_data

        def localize(string):
            try:
                relocalize = lambda match: loc_data[match.group(1)]
                localized = re.sub(r'\$(\w+)\$', relocalize, loc_data[string])
            except KeyError:
                localized = string
            return localized

        try:
            unlock_types = [unlock_type for unlock_type in next(iter(
                attribute for attribute in tech[tech_key]
                if attribute.keys()[0] == 'prereqfor_desc'
            ))['prereqfor_desc']]
            feature_unlocks = [localize(unlock.values()[0][0]['title'])
                               for unlock in unlock_types]
        except (StopIteration):
            feature_unlocks = []

        return feature_unlocks
