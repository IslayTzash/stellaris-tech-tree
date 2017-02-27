# -*- coding: utf-8 -*-

from pprint import pprint
import re
import ruamel.yaml as yaml
import sys

class WeightModifierParser:
    def __init__(self, loc_data):
        self.loc_data = loc_data

    def parse(self, modifier):
        try:
            factor = next(iter(key for key in modifier
                               if key.keys()[0] == 'factor'))['factor']
            adjustment = self._localize_factor(factor)
        except StopIteration:
            add = next(iter(line for line in modifier
                            if line.keys()[0] == 'add'))['add']
            adjustment = self._localize_add(add)

        unparsed_conditions = [line for line in modifier \
                               if line.keys()[0] not in ['factor', 'add']]
        conditions = []

        for condition in unparsed_conditions:
            condition = self._parse_condition(condition)
            conditions.append(condition)

        yaml_output = yaml.dump({adjustment: conditions}, indent=4,
                                default_flow_style=False,
                                allow_unicode=True).decode('utf-8')
        pseudo_yaml = re.sub(ur'(\xd7[\d.]+):\n\s*- ', r'(\1)',
                             yaml_output).replace('- ', u'• ')
        return pseudo_yaml


    def _parse_condition(self, condition):
        key = condition.keys()[0]
        value = condition[key]
        return getattr(self, '_localize_' + key.lower())(value)

    def _localize_factor(self, factor):
        return u'\xD7{}'.format(factor)

    def _localize_add(self, add):
        sign = '' if add == 0 else '+' if add > 0 else '-';
        return 'Add: {}{}'.format(sign, add)

    def _localize_has_ethic(self, value):
        ethic = self.loc_data[value]
        return 'Has {} Ethic'.format(ethic)

    def _localize_has_not_ethic(self, value):
        ethic = self.loc_data[value]
        return 'Does NOT have {} Ethic'.format(ethic)

    def _localize_has_policy_flag(self, value):
        policy_flag = self.loc_data[value]
        return 'Has {} Policy'.format(policy_flag)

    def _localize_has_trait(self, value):
        trait = self.loc_data[value]
        return 'Has {} Trait'.format(trait)

    def _localize_has_technology(self, value):
        try:
            technology = self.loc_data[value]
        except KeyError:
            technology = value

        return 'Has {} Technology'.format(technology)

    def _localize_has_not_technology(self, value):
        try:
            technology = self.loc_data[value]
        except KeyError:
            technology = value

        return 'Does NOT have {} Technology'.format(technology)

    def _localize_has_modifier(self, value):
        modifier = self.loc_data[value]
        return 'Has the {} modifier'.format(modifier)


    def _localize_is_country_type(self, value):
        return 'Is of the {} country type'.format(value)

    def _localize_ideal_planet_class(self, value):
        return 'Is ideal class'.format(value)

    def _localize_is_planet_class(self, value):
        planet_class = self.loc_data[value]
        return 'Is {}'.format(planet_class)

    def _localize_has_government(self, value):
        government = self.loc_data[value]
        return 'Has {}'.format(government)

    def _localize_is_colony(self, value):
        return 'Is a Colony' if value == 'yes' \
            else 'Is NOT a Colony'

    def _localize_has_federation(self, value):
        return 'Is in a Federation' if value == 'yes' \
            else 'Is NOT in a Federation'

    def _localize_num_owned_planets(self, value):
        operator, value = self._operator_and_value(value)
        return 'Number of owned planets is {} {}'.format(operator, value)

    def _localize_num_communications(self, value):
        operator, value = self._operator_and_value(value)
        return 'Number of owned planets is {} {}'.format(operator, value)

    def _localize_has_communications(self, value):
        return 'Has communications with your Empire'

    def _localize_is_ai(self, value):
        return 'Is AI controlled' if value == 'yes' else 'Is NOT AI controlled'

    def _localize_is_same_species(self, value):
        localized_value = 'Dominant' \
                          if value.lower() == 'root' \
                             else self.loc_data[value]
        return 'Is of the {} Species'.format(localized_value)

    def _localize_is_species(self, value):
        localized_value = 'Dominant' \
                          if value.lower() == 'root' \
                             else self.loc_data[value]
        article = 'an' if localized_value[0].lower() in 'aeiou' else 'a'

        return 'Is {} {}'.format(article, localized_value)

    def _localize_is_species_class(self, value):
        localized_value = self.loc_data[value]
        article = 'an' if localized_value[0].lower() in 'aeiou' else 'a'

        return 'Is {} {}'.format(article, localized_value)

    def _localize_is_enslaved(self, value):
        return 'Pop is enslaved' if value == 'yes' else 'Pop is NOT enslaved'

    def _localize_years_passed(self, value):
        operator, value = self._operator_and_value(value)
        return 'Number of years since game start is {} {}'.format(operator, value)

    def _localize_has_country_flag(self, value):
        return 'Has {} country flag'.format(value)

    def _localize_has_not_country_flag(self, value):
        return 'Does NOT have {} country flag'.format(value)

    def _localize_research_leader(self, values):
        leader = 'Research Leader ({})'.format(values[0]['area'].title())
        localized_conditions = []
        for condition in values[1:]:
            key = condition.keys()[0]
            value = condition[key]
            localized_condition = {
                'has_trait': lambda: self._localize_has_expertise(value),
                'has_level': lambda: self._localize_has_level(value)
            }[key]()
            localized_conditions.append(localized_condition)

        return {leader: localized_conditions}

    def _localize_has_level(self, value):
        operator, level = self._operator_and_value(value)
        return 'Skill level is {} {}'.format(operator, level)

    def _localize_has_expertise(self, value):
        expertise = self.loc_data[value]
        if expertise.startswith('Expertise'):
            truncated = expertise.replace('Expertise: ', '')
            condition = 'Is {} Expert'.format(truncated)
        else:
            condition = 'Is {}'.format(expertise)

        return condition

    def _localize_any_system_within_border(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any System within Borders': parsed_values}

    def _localize_is_in_cluster(self, value):
        return 'Is in a {} Cluster'.format(value)

    def _localize_any_country(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any Country': parsed_values}

    def _localize_any_owned_pop(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any Owned Pop': parsed_values}

    def _localize_any_owned_planet(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any Owned Planet': parsed_values}

    def _localize_any_tile(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any Tile': parsed_values}

    def _localize_has_blocker(self, value):
        blocker = self.loc_data[value]
        return 'Has {} Tile Blocker'.format(blocker)

    def _localize_any_neighbor_country(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any Neighbor Country': parsed_values}

    def _localize_has_resource(self, value):
        resource, amount = value[0]['type'], value[1]['amount']
        operator, amount = self._operator_and_value(amount)
        localized_resource = self.loc_data[resource]

        return 'Has {} {} {}'.format(operator, amount, localized_resource)


    def _localize_and(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'All of the following': parsed_values}

    def _localize_or(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'Any of the following': parsed_values}

    def _localize_nor(self, values):
        parsed_values = [self._parse_condition(value) for value in values]
        return {'None of the following': parsed_values}

    def _localize_not(self, value):
        key = value[0].keys()[0]
        nested_value = value[0][key]

        if key == 'OR':
            # Redirect to localization of NOR:
            return self._parse_condition({'NOR': nested_value})
        else:
            negated_key = key.replace('has_', 'has_not_')
            negated_condition = {negated_key: value[0][key]}
            return self._parse_condition(negated_condition)

    def _operator_and_value(self, data):
        if type(data) is int:
            operator, value = 'equal to', data
        elif type(data) is dict:
            operator = {
                '>': 'greater than',
                '<': 'less than'
            }[data.keys()[0]]
            value = data.values()[0]

        return operator, value
