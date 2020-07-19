# -*- coding: utf-8 -*-

import re
import ruamel.yaml as yaml
import sys

localization_map = {}
wm_at_vars = {}

def parse(modifier, loc_data, at_vars):
    global localization_map
    global wm_at_vars
    localization_map = loc_data
    wm_at_vars = at_vars

    # TODO: Entry is missing from localization
    if not 'BYPASS_LGATE' in localization_map:
        localization_map['BYPASS_LGATE'] = 'L-Gate'

    if len(modifier) == 1:
        modifier.append({'always': 'yes'})

    try:
        factor = next(iter(key for key in modifier
                           if list(key.keys())[0] == 'factor'))['factor']
        adjustment = _localize_factor(factor)
    except StopIteration:
        add = next(iter(line for line in modifier
                        if list(line.keys())[0] == 'add'))['add']
        adjustment = _localize_add(add)

    unparsed_conditions = [line for line in modifier \
                           if list(line.keys())[0] not in ['factor', 'add']]
    if len(unparsed_conditions) > 1:
        unparsed_conditions = [{'AND': unparsed_conditions}]

    conditions = [_parse_condition(condition)
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


def _parse_condition(condition):
    key = list(condition.keys())[0]
    value = condition[key]
    gkey = '_localize_' + key.lower()
    if gkey in globals():
        return globals()[gkey](value)
    else:
        print(" ** Please add localize function to weight_modifiers.py: " + gkey)
        return value


def _localize_federation(value):
    # TODO EXTEND?
    if type(value) is list and 2 == len(value):
        if 'has_federation_perk' in value[0]:
            perk = localization_map[value[0]['has_federation_perk']]
            if 'any_member' in value[1]:
                return 'Has Federation Perk: {} and any member {}'.format(perk, _localize_has_technology(value[1]['any_member'][0]['has_technology']))
    print(' ++ No _localize_federation for: {}'.format(repr(value)))
    return value


def _localize_has_origin(value):
    ethic = localization_map[value]
    return 'Has {} Origin'.format(ethic)


def _localize_factor(factor):
    global wm_at_vars
    if str(factor).startswith('@') and factor in wm_at_vars:
        factor = wm_at_vars[factor]
    return '\xD7{}'.format(factor)


def _localize_add(add):
    sign = '' if add == 0 else '+' if add > 0 else '-';
    return '{}{}'.format(sign, add)


def _localize_has_deposit(value):
    ethic = localization_map[value]
    return 'Has {} Deposit'.format(ethic)


def _localize_has_ethic(value):
    ethic = localization_map[value]
    return 'Has {} Ethic'.format(ethic)


def _localize_has_not_ethic(value):
    ethic = localization_map[value]
    return 'Does NOT have {} Ethic'.format(ethic)


def _localize_is_pacifist(value):
    return 'Is some degree of Pacifist' if value == 'yes' \
        else 'Is NOT some degree of Pacifist'


def _localize_is_militarist(value):
    return 'Is some degree of Militarist' if value == 'yes' \
        else 'Is NOT some degree of Militarist'

def _localize_is_egalitarian(value):
    return 'Is some degree of Egalitarian' if value == 'yes' \
        else 'Is NOT some degree of Egalitarian'

def _localize_is_authoritarian(value):
    return 'Is some degree of Authoritarian' if value == 'yes' \
        else 'Is NOT some degree of Authoritarian'

def _localize_is_materialist(value):
    return 'Is some degree of Materialist' if value == 'yes' \
        else 'Is NOT some degree of Materialist'


def _localize_is_spiritualist(value):
    return 'Is some degree of Spiritualist' if value == 'yes' \
        else 'Is NOT some degree of Spiritualist'

def _localize_is_xenophile(value):
    return 'Is some degree of Xenophile' if value == 'yes' \
        else 'Is NOT some degree of Xenophile'

def _localize_is_xenophobe(value):
    return 'Is some degree of Xenophobe' if value == 'yes' \
        else 'Is NOT some degree of Xenophobe'

def _localize_has_civic(value):
    civic = localization_map[value]
    return 'Has {} Government Civic'.format(civic)


def _localize_has_valid_civic(value):
    civic = localization_map[value]
    return 'Has {} Government Civic'.format(civic)


def _localize_has_not_civic(value):
    civic = localization_map[value]
    return 'Does NOT have {} Government Civic'.format(civic)


def _localize_has_ascension_perk(value):
    perk = localization_map[value]
    return 'Has {} Ascension Perk'.format(perk)


def _localize_has_megastructure(value):
    megastructure = localization_map[value]
    return 'Has Megatructure {}'.format(megastructure)


def _localize_has_policy_flag(value):
    if value in localization_map:
        policy_flag = localization_map[value]
    else:
        policy_flag = value
    return 'Has {} Policy'.format(policy_flag)


def _localize_has_trait(value):
    trait = localization_map[value]
    return 'Has {} Trait'.format(trait)

def _localize_pop_has_trait(value):
    trait = localization_map[value]
    return 'Population has {} Trait'.format(trait)

def _localize_has_authority(value):
    authority = localization_map[value]
    return 'Has {} Authority'.format(authority)

def _localize_has_not_authority(value):
    authority = localization_map[value]
    return 'Does NOT have {} Authority'.format(authority)

def _localize_host_has_dlc(dlc):
    # dlc = localization_map[value]
    return 'Host does has the {} DLC'.format(dlc)

def _localize_host_has_not_dlc(dlc):
    # dlc = localization_map[value]
    return 'Host does NOT have the {} DLC'.format(dlc)

def _localize_has_technology(value):
    try:
        technology = localization_map[value]
    except KeyError:
        technology = value

    return 'Has {} Technology'.format(technology)


def _localize_has_not_technology(value):
    try:
        technology = localization_map[value]
    except KeyError:
        technology = value

    return 'Does NOT have {} Technology'.format(technology)


def _localize_has_modifier(value):
    modifier = localization_map[value]
    return 'Has the {} modifier'.format(modifier)


def _localize_has_not_modifier(value):
    modifier = localization_map[value]
    return 'Does NOT have the {} modifier'.format(modifier)


def _localize_is_country_type(value):
    return 'Is of the {} country type'.format(value)


def _localize_ideal_planet_class(value):
    return 'Is ideal class'.format(value)


def _localize_is_planet_class(value):
    planet_class = localization_map[value]
    return 'Is {}'.format(planet_class)


def _localize_has_government(value):
    government = localization_map[value]
    return 'Has {}'.format(government)


def _localize_has_not_government(value):
    government = localization_map[value]
    return 'Does NOT have {}'.format(government)


def _localize_is_colony(value):
    return 'Is a Colony' if value == 'yes' \
        else 'Is NOT a Colony'


def _localize_is_ftl_restricted(value):
    return 'FTL is restricted' if value == 'yes' \
        else 'FTL is NOT restricted'

def _localize_has_any_megastructure_in_empire(value):
    return 'Has any Megastructure' if value == 'yes' \
        else 'Has NO Megastructures'


def _localize_allows_slavery(value):
    return 'Allows Slavery' if value == 'yes' \
        else 'Does NOT allow Slavery'


def _localize_has_federation(value):
    return 'Is in a Federation' if value == 'yes' \
        else 'Is NOT in a Federation'

def _localize_num_owned_planets(value):
    operator, value = _operator_and_value(value)
    return 'Number of owned planets is {} {}'.format(operator, value)

def _localize_count_owned_pops(value):
    operator, value = _operator_and_value(value[1]['count'])
    return 'Number of enslaved planets {} {}'.format(operator, value)


def _localize_count_starbase_sizes(value):
    starbase_size = localization_map[value[0]['starbase_size']]
    operator, value = _operator_and_value(value[1]['count'])
    return 'Number of Starbase {} is {} {}'.format(starbase_size, operator, value)
    

def _localize_num_communications(value):
    operator, value = _operator_and_value(value)
    return 'Number of owned planets is {} {}'.format(operator, value)

def _localize_num_districts(value):
    found = False
    if type(value) is list:
        for d in value:
            if 'type' in d:
                key = localization_map[d['type']]                
            elif 'value' in d:
                operator, value = _operator_and_value(d['value'])
                value = 'Number of {} is {} {}'.format(key, operator, value)
                found = True
                break
    else:
        print(' ** Could not parse num districts {}'.format(repr(value)))
        return repr(value)
    if not found:
        print(' ** Could not format _localize_num_districts: {}'.format(value))
    return value

def _localize_has_communications(value):
    return 'Has communications with your Empire'


def _localize_is_ai(value):
    return 'Is AI controlled' if value == 'yes' else 'Is NOT AI controlled'


def _localize_is_same_species(value):
    species = 'Dominant' \
              if value.lower() == 'root' \
                 else localization_map[value]
    return 'Is of the {} Species'.format(species)


def _localize_is_species(value):
    species = 'Dominant' \
              if value.lower() == 'root' \
                 else localization_map[value]
    article = 'an' if species[0].lower() in 'aeiou' else 'a'
    return 'Is {} {}'.format(article, species)


def _localize_is_species_class(value):
    species_class = localization_map[value]
    article = 'an' if species_class[0].lower() in 'aeiou' else 'a'
    return 'Is {} {}'.format(article, species_class)


def _localize_is_enslaved(value):
    return 'Pop is enslaved' if value == 'yes' else 'Pop is NOT enslaved'


def _localize_has_seen_any_bypass(value):
    loc_key = 'bypass_{}'.format(value).upper()
    if loc_key in localization_map:   # bypass_lgate ?
        bypass = localization_map[loc_key]
        if bypass.startswith('$'):
            bypass = localization_map[bypass.replace('$', '')]
    else:
        bypass = value
    return 'Has encountered a {}'.format(bypass)
    

def _localize_has_not_seen_any_bypass(value):
    loc_key = 'bypass_{}'.format(value).upper()
    bypass = localization_map[loc_key]
    if bypass.startswith('$'):
        bypass = localization_map[bypass.replace('$', '')]
    return 'Has NOT encountered a {}'.format(bypass)
    

def _localize_owns_any_bypass(value):
    loc_key = 'bypass_{}'.format(value).upper()
    bypass = localization_map[loc_key]
    if bypass.startswith('$'):
        bypass = localization_map[bypass.replace('$', '')]
    return 'Controls a system with a {}'.format(bypass)
    

def _localize_not_owns_any_bypass(value):
    loc_key = 'bypass_{}'.format(value).upper()
    bypass = localization_map[loc_key]
    if bypass.startswith('$'):
        bypass = localization_map[bypass.replace('$', '')]
    return 'Does NOT control a system with a {}'.format(bypass)
    

def _localize_years_passed(value):
    operator, value = _operator_and_value(value)
    return 'Number of years since game start is {} {}'.format(operator, value)


def _localize_not_years_passed(value):
    operator, value = _operator_and_value(value)
    return 'Number of years since game start is NOT {} {}'.format(operator, value)


def _localize_has_country_flag(value):
    return 'Has {} country flag'.format(value)


def _localize_has_not_country_flag(value):
    return 'Does NOT have {} country flag'.format(value)


def _localize_research_leader(values, negated=False):
    leader = 'Research Leader ({})'.format(values[0]['area'].title())
    if negated:
        leader = 'NOT ' + leader

    localized_conditions = []
    for condition in values[1:]:
        key = list(condition.keys())[0]
        value = condition[key]
        localized_condition = {
            'has_trait': lambda: _localize_has_expertise(value),
            'has_level': lambda: _localize_has_level(value)
        }[key]()
        localized_conditions.append(localized_condition)

    return {leader: localized_conditions}


def _localize_not_research_leader(values):
    return _localize_research_leader(values, negated=True)


def _localize_has_level(value):
    operator, level = _operator_and_value(value)
    return 'Skill level is {} {}'.format(operator, level)


def _localize_has_expertise(value):
    expertise = localization_map[value]
    if expertise.startswith('Expertise'):
        truncated = expertise.replace('Expertise: ', '')
        condition = 'Is {} Expert'.format(truncated)
    else:
        condition = 'Is {}'.format(expertise)

    return condition


def _localize_any_system_within_border(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any System within Borders': parsed_values}


def _localize_is_in_cluster(value):
    return 'Is in a {} Cluster'.format(value)


def _localize_any_country(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Country': parsed_values}

def _localize_any_relation(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Relation': parsed_values}


def _localize_any_owned_pop(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any empire Pop': parsed_values}


def _localize_any_pop(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Pop': parsed_values}


def _localize_not_any_owned_pop(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'NOT any owned Pop': parsed_values}


def _localize_any_owned_planet(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any owned Planet': parsed_values}


def _localize_any_planet(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Planet': parsed_values}

def _localize_any_planet_within_border(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Planet within Borders': parsed_values}

def _localize_not_any_owned_planet(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'NOT any owned Planet': parsed_values}


def _localize_any_tile(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Tile': parsed_values}


def _localize_has_blocker(value):
    blocker = localization_map[value]
    return 'Has {} Tile Blocker'.format(blocker)


def _localize_has_surveyed_class(value):
    return 'Has surveyed {}'.format(value)


def _localize_has_tradition(value):
    tradition = localization_map[value]
    return 'Has {} Tradition'.format(tradition)


def _localize_has_not_tradition(value):
    tradition = localization_map[value]
    return 'Does NOT have {} Tradition'.format(tradition)


def _localize_has_swapped_tradition(value):
    tradition = localization_map[value]
    return 'Has {} Swapped Tradition'.format(tradition)


def _localize_any_neighbor_country(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any Neighbor Country': parsed_values}


def _localize_has_resource(value):
    resource, amount = value[0]['type'], value[1]['amount']
    operator, amount = _operator_and_value(amount)
    localized_resource = localization_map[resource]

    return 'Has {} {} {}'.format(operator, amount, localized_resource)


def _localize_always(value):
    return 'Always' if value == 'yes' else 'Never'


def _localize_and(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'All of the following': parsed_values}


def _localize_or(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Any of the following': parsed_values}


def _localize_nor(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'None of the following': parsed_values}


def _localize_not(value):
    key = list(value[0].keys())[0]
    nested_value = value[0][key]

    if key == 'OR':
        # Redirect to localization of NOR:
        negation = _parse_condition({'NOR': nested_value})
    else:
        negated_key = key.replace('has_', 'has_not_') if 'has_' in key \
                      else 'not_' + key
        negated_condition = {negated_key: value[0][key]}
        negation = _parse_condition(negated_condition)

    return negation


def _localize_not_and(values):
    parsed_values = [_parse_condition(value) for value in values]
    return {'Not all of the following': parsed_values}


# TODO: Does this help or just make tooltips longer?
def _lookup_comparison_operator(value):
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


def _operator_and_value(data):
    if type(data) is int:
        operator = 'equal to'
        value = data
    elif type(data) is dict:
        symbol = list(data.keys())[0]
        operator = _lookup_comparison_operator(symbol)
        value = list(data.values())[0]
    else:
        print(" ** Unsupported data type {} {}".format(type(data), repr(data)))
        operator = ""
        value = data

    return operator, value


# NSC mod scripted triggers:
def _localize_is_playable_country(value):
    return 'Is playable Country' if value == 'yes' \
        else 'Is NOT playable Country'

# New Horizons mod scripted triggers:
def _localize_original_series_ships_era(value):
    return 'Original Series ships era' if value == 'yes' \
        else 'NOT Original Series ships era'


def _localize_motion_picture_ships_era(value):
    return 'Motion Picture ships era' if value == 'yes' \
        else 'NOT Motion Picture ships era'


def _localize_is_borg_empire(value):
    return 'Is the Borg Empire' if value == 'yes' \
        else 'Is NOT the Borg Empire'


def _localize_is_nomadic_empire(value):
    return 'Is the Nomadic Empire' if value == 'yes' \
        else 'Is NOT the Nomadic Empire'


def _localize_is_machine_cybernetic_empire(value):
    return 'Is the Machine Cybernetic Empire' if value == 'yes' \
        else 'Is NOT the Machine Cybernetic Empire'

def _localize_is_machine_empire(value):
    return 'Is the Machine Empire' if value == 'yes' \
        else 'Is NOT the Machine Empire'

def _localize_is_lithoid_empire(value):
    return 'Is the Lithoid Empire' if value == 'yes' \
        else 'Is NOT the Lithoid Empire'        

def _localize_is_temporal_masters(value):
    return 'Is the Temporal Masters' if value == 'yes' \
        else 'Is NOT the Temporal Masters'


def _localize_is_mirror_version_empire(value):
    return 'Is a Mirror Universe Empire' if value == 'yes' \
        else 'Is NOT a Mirror Universe Empire'


def _localize_has_espionage_agency(value):
    return 'Has an Espionage Agency' if value == 'yes' \
        else 'Does NOT have an Espionage Agency'


def _localize_is_master_geneticist(value):
    return 'Has Master Geneticist Trait' if value == 'yes' \
        else 'Does NOT have Master Geneticist Trait'


def _localize_no_psionic_potential(value):
    return 'Does NOT have Psionic Potential' if value == 'yes' \
        else 'Has Psionic Potential'


def _localize_is_telepathic_empire(value):
    return 'Is a Telepathic Empire' if value == 'yes' \
        else 'Is NOT a Telepathic Empire'


def _localize_is_non_standard_colonization(value):
    return 'Is a non-standard colonization' if value == 'yes' \
        else 'Is a standard colonization'


def _localize_uses_photonic_weapons_any_torp(value):
    return 'Uses Photonic Torpedoes' if value == 'yes' \
        else 'Does NOT use Photonic Torpedoes'


def _localize_uses_plasma_weapons_any_torp(value):
    return 'Uses Plasma Torpedoes' if value == 'yes' \
        else 'Does NOT use Plasma Torpedoes'


def _localize_uses_phaser_weapons_any(value):
    return 'Uses Phasers' if value == 'yes' \
        else 'Does NOT use Phasers'


def _localize_uses_disruptor_weapons_any(value):
    return 'Uses Disruptors' if value == 'yes' \
        else 'Does NOT use Disruptors'


def _localize_uses_disruptor_weapons(value):
    return 'Uses Disruptors' if value == 'yes' \
        else 'Does NOT use Disruptors'

def _localize_uses_plasma_disruptor_weapons(value):
    return 'Uses Plasma Disruptors' if value == 'yes' \
        else 'Does NOT use Plasma Disruptors'

def _localize_uses_antiproton_weapons_any(value):
    return 'Uses Anti-Proton Weapons' if value == 'yes' \
        else 'Does NOT use Anti-Proton Weapons'

def _localize_is_sapient(value):
    return 'This Species is pre-sapient' if value == 'yes' \
        else 'This Species is NOT pre-sapient'

def _localize_uses_cloaks(value):
    return 'Uses Cloaking' if value == 'yes' \
        else 'Does NOT use Cloaking'
