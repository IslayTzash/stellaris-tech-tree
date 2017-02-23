#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lex import tokens
from os import listdir, path
from ply.yacc import yacc
from pprint import pprint
import codecs
import json
import re
import ruamel.yaml as yaml
import sys

def p_script(tokens):
    'script : statements'
    tokens[0] = tokens[1]


def p_statement_statements(tokens):
    'statements : statement statements'
    tokens[0] = tokens[1] + tokens[2]


def p_statements_empty(tokens):
    'statements : empty'
    tokens[0] = []


def p_empty(tokens):
    'empty :'
    pass


def p_statement_var_assign(tokens):
    'statement : VARIABLE EQUALS NUMBER'
    number = int(tokens[3]) if '.' not in tokens[3] else float(tokens[3])
    tokens[0] = [{tokens[1]: number}]


def p_statement_binop(tokens):
    'statement : binop'
    tokens[0] = tokens[1]


def p_expression_variable(tokens):
    'expression : VARIABLE'
    tokens[0] = tokens[1]


def p_key(tokens):
    '''key : STRING
           | BAREWORD'''
    tokens[0] = tokens[1]


def p_expression_key(tokens):
    'expression : key'
    tokens[0] = tokens[1]

def p_expression_number(tokens):
    'expression : NUMBER'
    tokens[0] = tokens[1]

def p_keys(tokens):
    'keys : key keys'
    tokens[0] = [tokens[1]] + tokens[2] if type(tokens[1]) is str else \
                [tokens[1], tokens[2]]


def p_keys_empty(tokens):
    'keys : empty'
    tokens[0] = []


def p_binop(tokens):
    '''binop : key EQUALS expression
             | key GTHAN expression
             | key LTHAN expression'''
    operator = tokens[2]

    if re.match(r'^-?\d+$', str(tokens[3])):
        roperand = int(tokens[3])
    elif re.match(r'^-?\d+\.\d+$', str(tokens[3])):
        roperand = float(tokens[3])
    else:
        roperand = tokens[3]


    tokens[0] = [{tokens[1]: roperand}] if operator == '=' else \
                [{tokens[1]: {operator: roperand}}]


def p_list(tokens):
    '''list : LBRACE keys RBRACE'''
    tokens[0] = tokens[2]


def p_expression_list(tokens):
    'expression : list'
    tokens[0] = tokens[1]


def p_block(tokens):
    'block : LBRACE statements RBRACE'
    tokens[0] = tokens[2]


def p_expression_block(tokens):
    'expression : block'
    tokens[0] = tokens[1]


def p_error(p):
    raise Exception("Syntax error in input: {}".format(str(p)))

try:
    tree_name = sys.argv[1]
except IndexError:
    sys.exit('No Stellaris tree name provided!')


try:
    directories = sys.argv[2:]
except IndexError:
    sys.exit('No Stellaris game directories provided!')

tech_file_paths = []
loc_file_paths = []
for directory in directories:
    tech_dir = path.join(directory, 'common/technology')
    tech_file_paths += [path.join(tech_dir, filename) for filename
                  in listdir(tech_dir)
                  if path.isfile(path.join(tech_dir, filename))]

    loc_dir = path.join(directory, 'localisation')
    loc_file_paths += [path.join(loc_dir, filename) for filename
                      in listdir(loc_dir)
                      if path.isfile(path.join(loc_dir, filename))
                      and filename.endswith('l_english.yml')
                      and 'event' not in filename
                      and 'horizonsignal' not in filename]

tech_data = ''
for file_path in tech_file_paths:
    sys.stderr.write('Processing {} ...\n'.format(path.basename(file_path)))
    tech_data += open(file_path).read()

script = yacc().parse(tech_data)
technologies = []
at_vars = {}

def localized_strings():
    loc_data = { }
    for file_path in loc_file_paths:
        sys.stderr.write('Processing {} ...\n'.format(path.basename(file_path)))
        not_yaml = codecs.open(file_path, 'r', 'utf-8-sig').read()
        still_not_yaml = re.sub(ur'§[A-Z!]', '', not_yaml)
        hardly_yaml = re.sub(r'(?<=\w):\d (?=")', ': ', still_not_yaml)
        resembles_yaml = re.sub(ur'''(?<=[a-z ]{2}|\\n| "|[.,] )"(.+?)"''',
                          r'\"\1\"',
                             hardly_yaml)
        actual_yaml = re.sub(r'^ ', '  ', resembles_yaml, flags=re.M)

        try:
            file_data = yaml.load(actual_yaml, Loader=yaml.Loader)
            loc_map = file_data['l_english']
            loc_data.update(loc_map)
        except (yaml.parser.ParserError) as error:
            sys.stderr.write(str(error) + '\n')
            sys.stderr.write("Could't process {}.\n".format(path.basename(file_path)))
            continue

    return loc_data


def is_start_tech(tech):
    key = tech.keys()[0]
    if key in ['tech_lasers_1', 'tech_mass_drivers_1', 'tech_missiles_1']:
        value = True
    else:
        try:
            yes_no = next(iter(key for key in tech[key] if key.keys()[0] == 'category'))['start_tech'][0]
            value = True if value == 'yes' else False
        except KeyError:
            value = False

    return value

def prerequisite(tech):
    key = tech.keys()[0]
    if key in ['tech_biolab_1', 'tech_physics_lab_1',
               'tech_engineering_lab_1']:
        return 'tech_basic_science_lab_1'

    try:
        value = next(iter(
            subkey for subkey in tech[key] if subkey.keys()[0] == 'prerequisites'
        ))['prerequisites'][0]
    except StopIteration:
        value = None

    return value

def tier(tech):
    key = tech.keys()[0]
    if key in ['tech_lasers_1', 'tech_mass_drivers_1', 'tech_missiles_1']:
        tier = 0
    else:
        tier = next(iter(key for key in tech[key] if key.keys()[0] == 'tier'))['tier']

        try:
            weight_var = next(iter(key for key in tech[key] if key.keys()[0] == 'weight'))['weight']
            weight_tier = int(re.match(r'@tier(\d)weight\d', weight_var).group(1))
            if weight_tier > tier:
                tier = weight_tier
        except (TypeError, AttributeError, StopIteration):
            pass

    return tier

def subtier(tech):
    try:
        weight_var = next(iter(key for key in tech[key] if key.keys()[0] == 'weight'))['weight']
        subtier = int(re.match(r'@tier\dweight(\d)', weight_var).group(1))
    except TypeError:
        subtier = 1
    except AttributeError:
        subtier = 1
    except StopIteration:
        subtier = 1

    return subtier

def cost(tech):
    string = next(iter(key for key in tech[key] if key.keys()[0] == 'cost'))['cost']
    return at_vars[string] if str(string).startswith('@') else string


def weight(tech):
    try:
        string = next(iter(key for key in tech[key] if key.keys()[0] == 'weight'))['weight']
    except StopIteration:
        string = 0
    return at_vars[string] if str(string).startswith('@') else string


loc_data = localized_strings()

for tech in script:
    if tech.keys()[0].startswith('@'):
        at_var = tech.keys()[0]
        at_vars[at_var] = tech[at_var]
        continue

    key = tech.keys()[0]

    if 'akx_' in key:
        continue

    area = next(iter(key for key in tech[key] if key.keys()[0] == 'area'))['area']
    category = next(iter(key for key in tech[key] if key.keys()[0] == 'category'))['category'][0]
    weight_modifiers = next(iter(
        key for key in tech[key] if key.keys()[0] == 'weight_modifier'),
                            {'weight_modifier': [None]})['weight_modifier']

    try:
        name = loc_data[key]
    except KeyError:
        name = key

    try:
        description = loc_data[key + '_desc']
        description = loc_data[description.replace('$', '')] if \
                      description.startswith('$') else \
                      description
    except KeyError:
        description = ''

    try:
        prereq = prerequisite(tech)
    except IndexError:
        print key
        prereq = None

    technologies.append({
        'key': key,
        'tier': tier(tech),
        'subtier': subtier(tech),
        'name': name,
        'desc': description,
        'cost': cost(tech),
        'weight': weight(tech),
        'weight_modifiers': weight_modifiers,
        'area': area.title(),
        'start_tech': is_start_tech(tech),
        'category': loc_data[category],
        'prerequisite': prereq
    })

jsonified = json.dumps(technologies, indent=2, separators=(',', ': '))
# print jsonified
open(path.join('public', tree_name, 'techs.json'), 'w').write(jsonified)
