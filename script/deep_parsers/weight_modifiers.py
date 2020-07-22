# -*- coding: utf-8 -*-

import re
import ruamel.yaml as yaml
import sys

class WeightModifiers:
    def __init__(self, localizer, at_vars):
        self._localizer = localizer
        self._at_vars = at_vars

    def parse(self, modifier):
        if len(modifier) == 1:
            modifier.append({'always': 'yes'})

        try:
            factor = next(iter(key for key in modifier
                            if list(key.keys())[0] == 'factor'))['factor']
            adjustment = self._localize_factor(factor)
        except StopIteration:
            add = next(iter(line for line in modifier
                            if list(line.keys())[0] == 'add'))['add']
            adjustment = self._localize_add(add)

        unparsed_conditions = [line for line in modifier \
                            if list(line.keys())[0] not in ['factor', 'add']]
        if len(unparsed_conditions) > 1:
            unparsed_conditions = [{'AND': unparsed_conditions}]

        conditions = [self._parse_condition(condition)
                    for condition
                    in unparsed_conditions]

        yaml_output = yaml.dump({adjustment: conditions}, indent=4,
                                default_flow_style=False,
                                allow_unicode=True)
        pseudo_yaml = re.sub(r'(\xd7[\d.]+):\n\s*- ', r'(\1)',
                            yaml_output).replace('- ', '• ')
        # print(repr(modifier).encode('utf-8'))
        # print(repr(pseudo_yaml).encode('utf-8'))
        # exit()
        return pseudo_yaml


    def _parse_condition(self, condition):
        key = list(condition.keys())[0]
        value = condition[key]
        gkey = '_localize_' + key.lower()
        f = getattr(self, gkey, None)
        if f:
            return f(value)
        else:
            print(" ** Please add localize function to weight_modifiers.py: " + gkey)
            return value

    ########################################################################################

    def _localize_basic_has_or_has_not(self, value, label, isPositive=True):
        """
        Has/Has Not display:
            Has <VALUE> <LABEL> -> Has Dark Matter Deposit
            Does NOT have <VALUE> <LABEL>

        Parameters
        ----------
        :param value: the value to localize
        :param label: a trailing category for the message
        :param isPositive: if false, render negated message
        """
        return "{} {} {}".format( "Has" if isPositive else "Does NOT have", self._localizer.get(value), label)

    def _localize_has_origin(self, value):
        return self._localize_basic_has_or_has_not(value, "Origin")

    def _localize_has_deposit(self, value):
        return self._localize_basic_has_or_has_not(value, "Deposit")

    def _localize_has_ethic(self, value):
        return self._localize_basic_has_or_has_not(value, "Ethic")

    def _localize_not_has_ethic(self, value):
        return self._localize_basic_has_or_has_not(value, "Ethic", False)

    def _localize_has_civic(self, value):
        return self._localize_basic_has_or_has_not(value, "Government Civic")

    def _localize_has_valid_civic(self, value):
        return self._localize_has_civic(value)

    def _localize_not_has_civic(self, value):
        return self._localize_basic_has_or_has_not(value, "Government Civic", False)

    def _localize_not_has_valid_civic(self, value):
        return self._localize_not_has_civic(value)

    def _localize_has_ascension_perk(self, value):
        return self._localize_basic_has_or_has_not(value, "Ascension Perk")

    def _localize_has_megastructure(self, value):
        return self._localize_basic_has_or_has_not(value, "Megatructure")

    def _localize_has_policy_flag(self, value):
        return self._localize_basic_has_or_has_not(value, "Policy")

    def _localize_has_trait(self, value):
        return self._localize_basic_has_or_has_not(value, "Trait")

    def _localize_has_authority(self, value):
        return self._localize_basic_has_or_has_not(value, "Authority")

    def _localize_not_has_authority(self, value):
        return self._localize_basic_has_or_has_not(value, "Authority", False)

    def _localize_has_technology(self, value):
        return self._localize_basic_has_or_has_not(value, "Technology")

    def _localize_not_has_technology(self, value):
        return self._localize_basic_has_or_has_not(value, "Authority", False)

    def _localize_has_modifier(self, value):
        return self._localize_basic_has_or_has_not(value, "Modifier")

    def _localize_not_has_modifier(self, value):
        return self._localize_basic_has_or_has_not(value, "Modifier", False)

    def _localize_has_country_flag(self, value):
        return self._localize_basic_has_or_has_not(value, "country flag")

    def _localize_not_has_country_flag(self, value):
        return self._localize_basic_has_or_has_not(value, "country flag", False)

    def _localize_has_blocker(self, value):
        return self._localize_basic_has_or_has_not(value, "Tile Blocker")

    def _localize_has_tradition(self, value):
        return self._localize_basic_has_or_has_not(value, "Tradition")

    def _localize_not_has_tradition(self, value):
        return self._localize_basic_has_or_has_not(value, "Tradition", False)

    def _localize_has_swapped_tradition(self, value):
        return self._localize_basic_has_or_has_not(value, "Swapped Tradition")

    def _localize_not_has_ancrel(self, value):
        return self._localize_basic_has_or_has_not(value, "Ancient Relic", False)

    ########################################################################################

    def _localize_basic_negatable_statement(self, value, statement):
        """
        Display a statement, remove the string "NOT " from the statement if value is "yes" 

        Parameters
        ----------
        :param value: value which should be "yes" when true
        :param statment: Basic statement to display, "NOT " may be removed from the statement
        """
        if value.lower() == 'yes':
            # Remove the NOT, also clean up some common oddness like "Does have " => "Has" / "Does use" => "Uses"
            return re.sub(r'^Does use', 'Uses', re.sub(r'^Does have', 'Has', re.sub(r'NOT ', '', statement)))
        else:
            return statement

    def _localize_is_pacifist(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Pacifist')

    def _localize_is_militarist(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Militarist')

    def _localize_is_egalitarian(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Egalitarian')

    def _localize_is_authoritarian(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Authoritarian')

    def _localize_is_materialist(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Materialist')

    def _localize_is_spiritualist(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Spiritualist')

    def _localize_is_xenophile(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Xenophile')

    def _localize_is_xenophobe(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT some degree of Xenophobe')

    def _localize_is_playable_country(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT playable Country')

    def _localize_original_series_ships_era(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT Original Series ships era')

    def _localize_original_series_ships_era(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT Motion Picture ships era')

    def _localize_is_borg_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Borg Empire')

    def _localize_is_nomadic_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Nomadic Empire')

    def _localize_is_machine_cybernetic_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Machine Cybernetic Empire')

    def _localize_is_machine_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Machine Empire')

    def _localize_is_lithoid_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Lithoid Empire')

    def _localize_is_temporal_masters(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT the Temporal Masters')

    def _localize_is_mirror_version_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT a Mirror Universe Empire')

    def _localize_has_espionage_agency(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT have an Espionage Agency')

    def _localize_is_master_geneticist(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT have Master Geneticist Trait')

    def _localize_is_telepathic_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT a Telepathic Empire')

    def _localize_uses_photonic_weapons_any_torp(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Photonic Torpedoes')

    def _localize_uses_plasma_weapons_any_torp(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Plasma Torpedoes')

    def _localize_uses_phaser_weapons_any(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Phasers')

    def _localize_uses_disruptor_weapons_any(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Disruptors')

    def _localize_uses_disruptor_weapons(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Disruptors')

    def _localize_uses_plasma_disruptor_weapons(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Plasma Disruptors')

    def _localize_uses_antiproton_weapons_any(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Anti-Proton Weapons')

    def _localize_is_sapient(self, value):
        return self._localize_basic_negatable_statement(value, 'This Species is NOT pre-sapient')

    def _localize_uses_cloaks(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT use Cloaking')

    def _localize_is_colony(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT a Colony')

    def _localize_is_ftl_restricted(self, value):
        return self._localize_basic_negatable_statement(value, 'FTL is NOT restricted')

    def _localize_has_any_megastructure_in_empire(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT have any Megastructures')

    def _localize_allows_slavery(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT allow Slavery')

    def _localize_has_federation(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT in a Federation')

    def _localize_is_enslaved(self, value):
        return self._localize_basic_negatable_statement(value, 'Pop is NOT enslaved')

    def _localize_has_communications(self, value):
        return self._localize_basic_negatable_statement(value, 'Does NOT have communications with your Empire')

    def _localize_ideal_planet_class(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT an ideal class')

    def _localize_is_ai(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT AI controlled')

    def _localize_is_galactic_community_member(self, value):
        return self._localize_basic_negatable_statement(value, 'Is NOT a galactic community member')

    ## These guys are backwards, leave them alone

    def _localize_no_psionic_potential(self, value):
        return 'Does NOT have Psionic Potential' if value == 'yes' \
            else 'Has Psionic Potential'

    def _localize_is_non_standard_colonization(self, value):
        return 'Is a non-standard colonization' if value == 'yes' \
            else 'Is a standard colonization'

    ########################################################################################

    def _localize_basic_container_rule(self, values, label):
        """
        This is just a container for more rules, parse them and bundle up child results

        Parameters
        ----------
        :param values: child rules
        :param label:  label to display before child rule tree
        """
        return {label: [self._parse_condition(value) for value in values]}

    def _localize_and(self, values):
        return self._localize_basic_container_rule(values, 'All of the following')

    def _localize_or(self, values):
        return self._localize_basic_container_rule(values, 'Any of the following')

    def _localize_nor(self, values):
        return self._localize_basic_container_rule(values, 'None of the following')

    def _localize_not_or(self, values):
        return self._localize_nor(values)

    def _localize_not_and(self, values):
        return self._localize_basic_container_rule(values, 'Not all of the following')

    def _localize_any_system_within_border(self, values):
        return self._localize_basic_container_rule(values, 'Any System within Borders')

    def _localize_not_any_system_within_border(self, values):
        return self._localize_basic_container_rule(values, 'No System within Borders')

    def _localize_any_system_planet(self, values):
        return self._localize_basic_container_rule(values, 'Any Planet in System')

    def _localize_any_country(self, values):
        return self._localize_basic_container_rule(values, 'Any Country')

    def _localize_any_relation(self, values):
        return self._localize_basic_container_rule(values, 'Any Relation')

    def _localize_any_owned_pop(self, values):
        return self._localize_basic_container_rule(values, 'Any empire Pop')

    def _localize_any_pop(self, values):
        return self._localize_basic_container_rule(values, 'Any Pop')

    def _localize_not_any_owned_pop(self, values):
        return self._localize_basic_container_rule(values, 'NOT any owned Pop')

    def _localize_any_owned_planet(self, values):
        return self._localize_basic_container_rule(values, 'Any owned Planet')

    def _localize_any_planet(self, values):
        return self._localize_basic_container_rule(values, 'Any Planet')

    def _localize_any_planet_within_border(self, values):
        return self._localize_basic_container_rule(values, 'Any Planet within Borders')

    def _localize_not_any_owned_planet(self, values):
        return self._localize_basic_container_rule(values, 'NOT any owned Planet')

    def _localize_any_tile(self, values):
        return self._localize_basic_container_rule(values, 'Any Tile')

    def _localize_any_neighbor_country(self, values):
        return self._localize_basic_container_rule(values, 'Any Neighbor Country')

    def _localize_federation(self, values):
        return self._localize_basic_container_rule(values, 'Federation')

    def _localize_any_member(self, values):
        return self._localize_basic_container_rule(values, 'Any Federation Member')

    ########################################################################################

    def _lookup_comparison_operator(self, value):
        if value == '>':
            return 'greater than'
        elif value == '<':
            return 'less than'
        elif value == '>=':
            return 'greater than or equal to'
        elif value == '<=':
            return 'less than or equal to'
        else:
            print(" ** cannot transform operator {}".format(repr(value)))
            return value

    def _operator_and_value(self, data):
        if type(data) is int:
            operator = 'equal to'
            value = data
        elif type(data) is dict:
            symbol = list(data.keys())[0]
            operator = self._lookup_comparison_operator(symbol)
            value = list(data.values())[0]
        else:
            print(" ** Unsupported data type {} {}".format(type(data), repr(data)))
            operator = ""
            value = data
        return (operator, value)

    def _localize_basic_operator_rule(self, values, label):
        """
        Call _operator_and_value() and print the operator description and values that are returned after the label string

        Parameters
        ----------
        :param values: rule with operator and value contents
        :param label:  label to display before parsed operator rule tree
        """
        (operator, value) = self._operator_and_value(values)
        return '{} {} {}'.format(label, operator, value)

    def _localize_num_owned_planets(self, value):
        return self._localize_basic_operator_rule(value, 'Number of owned planets is')

    def _localize_num_communications(self, value):
        return self._localize_basic_operator_rule(value, 'Number of owned planets is')  # TODO: RIGHT STRING?

    def _localize_years_passed(self, value):
        return self._localize_basic_operator_rule(value, 'Number of years since game start is')

    def _localize_not_years_passed(self, value):
        return self._localize_basic_operator_rule(value, 'Number of years since game start is NOT')

    def _localize_has_level(self, value):
        return self._localize_basic_operator_rule(value, 'Skill level is')

    def _localize_count_owned_pops(self, value):
        return self._localize_basic_operator_rule(value[1]['count'], 'Number of enslaved planets')

    def _localize_has_resource(self, value):
        return self._localize_basic_operator_rule(value[1]['amount'], self._localizer.get(value[0]['type']))

    def _localize_not_has_resource(self, value):
        return self._localize_basic_operator_rule(value[1]['amount'], 'No ' + self._localizer.get(value[0]['type']))  # ????

    def _localize_count_starbase_sizes(self, value):
        return self._localize_basic_operator_rule(value[1]['count'],
            'Number of {}'.format(self._localizer.get(value[0]['starbase_size'])))
            
    ########################################################################################

    def _singular_article(self, value):
        return 'a' if not value[0].lower() in 'aeiou' else 'an'

    # Simple rules with a string that gets looked up

    def _localize_pop_has_trait(self, value):
        return 'Population has {} Trait'.format(self._localizer.get(value))

    def _localize_host_has_dlc(self, dlc):
        return 'Host has the {} DLC'.format(dlc)

    def _localize_not_host_has_dlc(self, dlc):
        return 'Host does NOT have the {} DLC'.format(dlc)

    def _localize_is_country_type(self, value):
        return 'Is of the {} country type'.format(value)

    def _localize_is_planet_class(self, value):
        return 'Is {}'.format(self._localizer.get(value))

    def _localize_has_federation_perk(self, value):
        return 'Has {} Federation Perk'.format(self._localizer.get(value))

    def _localize_has_government(self, value):
        return 'Has {} Government'.format(self._localizer.get(value))

    def _localize_not_has_government(self, value):
        return 'Does NOT have {}'.format(self._localizer.get(value))

    def _localize_has_seen_any_bypass(self, value):
        return 'Has encountered a {}'.format(self._localizer.get_or_default('bypass_{}'.format(value), value))
        
    def _localize_not_has_seen_any_bypass(self, value):
        return 'Has NOT encountered a {}'.format(self._localizer.get_or_default('bypass_{}'.format(value), value))
        
    def _localize_owns_any_bypass(self, value):
        return 'Controls a system with a {}'.format(self._localizer.get_or_default('bypass_{}'.format(value), value))
        
    def _localize_not_owns_any_bypass(self, value):
        return 'Does NOT control a system with a {}'.format(self._localizer.get_or_default('bypass_{}'.format(value), value))

    def _localize_is_in_cluster(self, value):
        return 'Is in a {} Cluster'.format(value)

    def _localize_has_surveyed_class(self, value):
        return 'Has surveyed {}'.format(value)

    def _localize_is_species_class(self, value):
        species_class = self._localizer.get(value)
        return 'Is {} {}'.format(self._singular_article(species_class), species_class)

    ########################################################################################

    def _localize_factor(self, factor):
        """Numeric factor for each tech"""
        if str(factor).startswith('@') and factor in self._at_vars:
            factor = self._at_vars[factor]
        val = '\xD7{}'.format(factor)        
        if not '.' in val:  # Add .0 to integers to keep sizes similar
            val += '.0'
        return val


    def _localize_always(self, value):
        return 'Always' if value == 'yes' else 'Never'


    def _localize_not(self, value):
        key = list(value[0].keys())[0]
        return self._parse_condition({'not_' + key: value[0][key]})


    def _localize_add(self, add):
        sign = '' if add == 0 else '+' if add > 0 else '-'
        return '{}{}'.format(sign, add)


    def _localize_num_districts(self, value):
        found = False
        if type(value) is list:
            for d in value:
                if 'type' in d:
                    key = self._localizer.get(d['type'])
                elif 'value' in d:
                    (operator, value) = self._operator_and_value(d['value'])
                    value = 'Number of {} is {} {}'.format(key, operator, value)
                    found = True
                    break
        else:
            print(' ** Could not parse num districts {}'.format(repr(value)))
            return repr(value)
        if not found:
            print(' ** Could not format _localize_num_districts: {}'.format(value))
        return value


    def _localize_is_same_species(self, value):
        species = 'Dominant' \
                if value.lower().startswith('root') \
                    else self._localizer.get(value)
        return 'Is of the {} Species'.format(species)


    def _localize_research_leader(self, values, negated=False):
        leader = 'Research Leader ({})'.format(values[0]['area'].title())
        if negated:
            leader = 'NOT ' + leader

        localized_conditions = []
        for condition in values[1:]:
            key = list(condition.keys())[0]
            value = condition[key]
            localized_condition = {
                'has_trait': lambda: self._localize_has_expertise(value),
                'has_level': lambda: self._localize_has_level(value)
            }[key]()
            localized_conditions.append(localized_condition)

        return {leader: localized_conditions}


    def _localize_not_research_leader(self, values):
        return self._localize_research_leader(values, negated=True)


    def _localize_has_expertise(self, value):
        expertise = self._localizer.get(value)
        if expertise.startswith('Expertise'):
            truncated = expertise.replace('Expertise: ', '')
            condition = 'Is {} Expert'.format(truncated)
        else:
            condition = 'Is {}'.format(expertise)
        return condition

