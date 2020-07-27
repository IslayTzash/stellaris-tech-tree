#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lex import tokens

import ply.yacc
import re

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

def p_key(tokens):
    '''key : STRING
           | BAREWORD'''
    tokens[0] = tokens[1]

def p_keys(tokens):
    'keys : key keys'
    tokens[0] = [tokens[1]] + tokens[2] if type(tokens[1]) is str else [tokens[1], tokens[2]]

def p_keys_empty(tokens):
    'keys : empty'
    tokens[0] = []

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

def p_expression_key(tokens):
    'expression : key'
    tokens[0] = tokens[1]

def p_expression_number(tokens):
    'expression : NUMBER'
    tokens[0] = tokens[1]

def p_binop(tokens):
    '''binop : key EQUALS expression
             | key GTHAN expression
             | key LTHAN expression
             | key GTEQ expression
             | key LTEQ expression'''
    operator = tokens[2]

    if re.match(r'^-?\d+$', str(tokens[3])):
        roperand = int(tokens[3])
    elif re.match(r'^-?\d+\.\d+$', str(tokens[3])):
        roperand = float(tokens[3])
    else:
        roperand = tokens[3]


    tokens[0] = [{tokens[1]: roperand}] if operator == '=' else [{tokens[1]: {operator: roperand}}]

def p_list(tokens):
    '''list : LBRACE keys RBRACE'''
    tokens[0] = tokens[2]

def p_list_empty(tokens):
    '''list : LBRACE RBRACE'''
    tokens[0] = []

def p_list_double_wrapped(tokens):
    '''list : LBRACE LBRACE keys RBRACE RBRACE'''
    tokens[0] = tokens[3]

def p_expression_list(tokens):
    'expression : list'
    tokens[0] = tokens[1]

def p_block(tokens):
    'block : LBRACE statements RBRACE'
    tokens[0] = tokens[2]

def p_block_empty(tokens):
    'block : LBRACE RBRACE'
    tokens[0] = []

def p_block_double_wrapped(tokens):
    'block : LBRACE LBRACE statements RBRACE RBRACE'
    tokens[0] = tokens[3]

def p_expression_block(tokens):
    'expression : block'
    tokens[0] = tokens[1]

def p_error(p):
    raise Exception("Syntax error in input: {}".format(str(p)))

def get_parser():
    return ply.yacc.yacc()

class STTYacc:
    def __init__(self):
        self.yacc_parser = get_parser()

    def parse(self, contents):
        return self.yacc_parser.parse(contents)
