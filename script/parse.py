from lex import tokens
from os import listdir, path
from ply.yacc import yacc
from pprint import pprint
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
    directory = sys.argv[1]
except IndexError:
    sys.exit('No Stellaris technology directory provided!')

file_paths = [path.join(directory, filename) for filename
             in listdir(directory)
             if path.isfile(path.join(directory, filename))]
data = ''
for file_path in file_paths:
    sys.stderr.write('Processing {} ...\n'.format(path.basename(file_path)))
    data += open(file_path).read()

script = yacc().parse(data)
technologies = []
at_vars = {}

def localized_strings():
    yaml_file = open('/home/richard/stellaris/game/localisation/technology_l_english.yml')
    bad_yaml = yaml_file.read()
    good_yaml = re.sub(r'^ ', '  ',
                       re.sub(r'(?<!(?:: |[\\\w.]{2}| "))"([\w ]+)"', r'\"\1\"',
                              re.sub(r'(?<=\w):\d (?=")', ': ', bad_yaml)), flags=re.M)

    return yaml.load(good_yaml, Loader=yaml.Loader)['l_english']


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


localized = localized_strings()

for tech in script:
    if tech.keys()[0].startswith('@'):
        at_var = tech.keys()[0]
        at_vars[at_var] = tech[at_var]
        continue

    key = tech.keys()[0]
    area = next(iter(key for key in tech[key] if key.keys()[0] == 'area'))['area']
    category = next(iter(key for key in tech[key] if key.keys()[0] == 'category'))['category'][0]
    weight_modifiers = next(iter(
        key for key in tech[key] if key.keys()[0] == 'weight_modifier'),
                            {'weight_modifier': [None]})['weight_modifier']

    try:
        replaceable_description = localized[key + '_desc']
        description = localized[replaceable_description.replace('$', '')] if \
                      replaceable_description.startswith('$') else \
                      replaceable_description
    except KeyError:
        description = ''

    try:
        technologies.append({
            'key': key,
            'tier': tier(tech),
            'subtier': subtier(tech),
            'name': localized[key],
            'desc': description,
            'cost': cost(tech),
            'weight': weight(tech),
            'weight_modifiers': weight_modifiers,
            'area': area.title(),
            'start_tech': is_start_tech(tech),
            'category': localized[category],
            'prerequisite': prerequisite(tech)
        })
    except KeyError:
        continue

jsonified = json.dumps(technologies, indent=2, separators=(',', ': '))
# print jsonified
open('public/techs.json', 'w').write(jsonified)
