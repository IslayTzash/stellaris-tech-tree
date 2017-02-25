#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from lex import tokens
from os import listdir, path
from ply.yacc import yacc
from pprint import pprint
import argparse
import codecs
import json
import operator
import re
import ruamel.yaml as yaml
import sys


# Process CLI arguments:
def valid_label(label):
    if not re.match(r'^\w+$', label):
        raise argparse.ArgumentTypeError('Must match [a-z0-9_]')

    return label.lower()


def valid_dirs(directory):
    if not path.isdir(directory):
        message = "'{}' not found or not a directory".format(directory)
        raise argparse.ArgumentTypeError(message)

    return directory

arg_parser = argparse.ArgumentParser(
    description='Parse Stellaris tech and localization files')
arg_parser.add_argument('label', type=valid_label)
arg_parser.add_argument('directories', nargs='+', type=valid_dirs)

args = arg_parser.parse_args()
tree_label = args.label
directories = args.directories

def eprint(string):
    sys.stderr.write(string + '\n')


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


def parse_weight_modifier(modifier):
    pass

tech_file_paths = []
loc_file_paths = []
tech_filenames = set()
skip_terms = ['events?', 'tutorials?', 'pop_factions?', 'name_lists?',
              'messages?', 'mandates?', 'modifiers?', 'projects?', 'sections?',
              'triggers?', 'effects?', 'edicts?', 'traits?']
has_skip_term = re.compile(r'(?:{})_'.format('|'.join(skip_terms)))
for directory in directories:
    tech_dir = path.join(directory, 'common/technology')
    eprint('Loading {} ...'.format(tech_dir))
    for filename in listdir(tech_dir):
        file_path = path.join(tech_dir, filename)
        if not path.isfile(file_path):
            continue

        # If filename already loaded, replace old one with new:
        if filename in tech_filenames:
            path_to_delete = next(iter(
                file_path for file_path
                in tech_file_paths
                if path.basename(file_path) == filename
            ))
            eprint('Removing {} ...'.format(path_to_delete))
            tech_file_paths.remove(path_to_delete)

        tech_filenames.add(filename)
        tech_file_paths.append(path.join(tech_dir, filename))

    loc_dir = path.join(directory, 'localisation')
    loc_file_paths += [path.join(loc_dir, filename) for filename
                      in listdir(loc_dir)
                      if path.isfile(path.join(loc_dir, filename))
                      and filename.endswith('_l_english.yml')
                      and not has_skip_term.search(filename)]

tech_data = ''
for file_path in tech_file_paths:
    eprint('Processing {} ...'.format(path.basename(file_path)))
    tech_data += open(file_path).read()

script = yacc().parse(tech_data)
at_vars = {}

def localized_strings():
    loc_data = { }
    for file_path in loc_file_paths:
        eprint('Processing {} ...'.format(path.basename(file_path)))
        not_yaml_lines = codecs.open(file_path, 'r', 'utf-8-sig').readlines()
        not_yaml = ''
        for line in not_yaml_lines:
            quote_instances = [i for i, char in enumerate(line)
                               if char == u'"']

            if len(quote_instances) >= 2:
                # Some lines have invalid data after terminal quote:
                last = quote_instances[-1]
                line = line[:last + 1] + '\n'

                if len(quote_instances) > 2:
                    second = quote_instances[1]
                    line = line[0:second] \
                           + line[second:last].replace(u'"', ur'\"') \
                           + line[last:]

            not_yaml += line

        still_not_yaml = re.sub(ur'§[A-Z!]', '', not_yaml)
        resembles_yaml = re.sub(r'(?<=\w):\d (?=")', ': ', still_not_yaml)
        actual_yaml = re.sub(r'^ +', '  ', resembles_yaml, flags=re.M)

        file_data = yaml.load(actual_yaml, Loader=yaml.Loader)
        loc_map = file_data['l_english']
        loc_data.update(loc_map)

    return loc_data


def is_start_tech(tech):
    try:
        yes_no = next(iter(key for key in tech[key]
                           if key.keys()[0] == 'start_tech'))['start_tech']
        value = True if yes_no == 'yes' else False
    except StopIteration:
        value = True if tier(tech) == 0 else False

    return value

def is_dangerous(tech):
    try:
        yes_no = next(iter(key for key in tech[key]
                           if key.keys()[0] == 'is_dangerous'))['is_dangerous']
        value = True if yes_no == 'yes' else False
    except StopIteration:
        value = False

    return value

def is_rare(tech):
    try:
        yes_no = next(iter(key for key in tech[key]
                           if key.keys()[0] == 'is_rare'))['is_rare']
        value = True if yes_no == 'yes' else False
    except StopIteration:
        value = False

    return value

def prerequisite(tech):
    tech_key = tech.keys()[0]
    if key in ['tech_biolab_1', 'tech_physics_lab_1',
               'tech_engineering_lab_1']:
        return 'tech_basic_science_lab_1'

    try:
        value = next(iter(
            subkey for subkey in tech[tech_key]
            if subkey.keys()[0] == 'prerequisites'
        ))['prerequisites'][0]
    except (StopIteration, IndexError):
        value = None

    return value

def tier(tech):
    tier = next(
        iter(key for key in tech[key] if key.keys()[0] == 'tier')
    )['tier']

    return tier

def cost(tech):
    string = next(iter(key for key in tech[key] if key.keys()[0] == 'cost'))['cost']
    return at_vars[string] if str(string).startswith('@') else string


def base_weight(tech):
    tech_key = tech.keys()[0]

    try:
        string = next(iter(key for key in tech[key] if key.keys()[0] == 'weight'))['weight']
        weight = at_vars[string] \
                      if str(string).startswith('@') \
                      else string
    except StopIteration:
        weight = 0

    return weight

def base_factor(tech):
    try:
        string = next(
            iter(key for key in tech[key]
                 if key.keys()[0] == 'weight_modifier')
        )['weight_modifier'][0]['factor']
        factor = at_vars[string] \
                      if str(string).startswith('@') \
                         else string
    except (StopIteration, KeyError, IndexError):
        factor = 1.0

    return float(factor)


loc_data = localized_strings()
technologies = []

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

    tech_base_weight = base_weight(tech)
    tech_base_factor = base_factor(tech)
    try:
        modifier_list = next(iter(key for key in tech[key]
                                  if key.keys()[0] == 'weight_modifier')
        )['weight_modifier']
        weight_modifiers = modifier_list[1:] \
                           if modifier_list[0].keys() == ['factor'] \
                              else modifier_list

    except(StopIteration, KeyError, IndexError):
        weight_modifiers = []

    if not is_start_tech(tech) \
       and tech_base_weight * tech_base_factor == 0 \
       and len(weight_modifiers) == 0:
        continue


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

    technologies.append({
        'key': key,
        'tier': tier(tech),
        'name': name,
        'desc': description,
        'cost': cost(tech),
        'base_factor': tech_base_factor,
        'base_weight': tech_base_weight,
        'weight_modifiers': weight_modifiers,
        'area': area,
        'start_tech': is_start_tech(tech),
        'is_rare': is_rare(tech),
        'is_dangerous': is_dangerous(tech),
        'category': loc_data[category],
        'prerequisite': prerequisite(tech)
    })

technologies.sort(key=operator.itemgetter('tier'))
technologies.sort(
    key=lambda tech: {'physics': 1, 'society': 2, 'engineering': 3}[tech['area']])
jsonified = json.dumps(technologies, indent=2, separators=(',', ': '))
# print jsonified
open(path.join('public', tree_label, 'techs.json'), 'w').write(jsonified)
