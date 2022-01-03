#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import json
import re
import ruamel
import sys

from os import listdir, path

from configuration import Configuration
from game_objects import Localizer, Technology, TechnologyJSONEncoder
# These are accessed indirectly but must be imported
from game_objects import Army, ArmyAttachment, BuildablePop, Building, \
    Component, Edict, Policy, Resource, SpaceportModule, TileBlocker
from yacc import STTYacc

class Parser:

    # Dictionary keys
    ARMY = 'Army'
    ARMY_ATTACHMENT = 'ArmyAttachment'
    BUILDABLE_POP = 'BuildablePop'
    BUILDING = 'Building'
    COMPONENT = 'Component'
    EDICT = 'Edict'
    POLICY = 'Policy'
    RESOURCE = 'Resource'
    SPACEPORT_MODULE = 'SpaceportModule'
    TILE_BLOCKER = 'TileBlocker'
    TECHNOLOGY = 'Technology'

    CLASS = 'class'
    DIR = 'dir'
    DATA = 'data'
    PARSED_DATA = 'parsed_data'
    SKIP_PARSE = 'skip_parse'

    # Special handling for known modules
    NEW_HORIZONS = 'new_horizons'

    def get_file_paths(self, directory):
        if not path.isdir(directory):
            return []

        file_paths = []
        for filename in listdir(directory):
            file_path = path.join(directory, filename)
            if (not path.isfile(file_path)
                or 'README' in file_path
                or not file_path.endswith('.txt')):
                    continue

            # If filename already loaded, replace old one with new:
            path_to_delete = next(iter(
                    file_path for file_path
                    in file_paths
                    if path.basename(file_path) == filename
                ), None)
            if path_to_delete is not None:
                print('replacing {} ...'.format(path.basename(path_to_delete)))
                file_paths.remove(path_to_delete)

            file_paths.append(path.join(directory, filename))

        return file_paths

    def read_yaml_file(self, file_path):
        # Coerce Paradox's bastardized YAML into compliance
        input = ''
        for line in codecs.open(file_path, 'r', 'utf-8-sig').readlines():
            quote_instances = [i for i, char in enumerate(line) if char == '"']
            if len(quote_instances) >= 2:
                # Some lines have invalid data after terminal quote.  Truncate at final quote
                # Some lines have escaped quotes as "" or \" or non-escaped quotes.  Convert all inner quotes to \" escaping.
                last = quote_instances[-1]
                if len(quote_instances) == 2:
                    line = line[:last + 1] + '\n'
                else:
                    second = quote_instances[1]
                    if line[second-1] == "\\":
                        second = second - 1
                    line = line[0:second] + re.sub(r"""(^|[^\\])["]+""", r'\g<1>\\"', line[second:last]) + '"\n'
            input += line

        if self.config.mod == Parser.NEW_HORIZONS:
            input = re.sub(r'\\T', 'T', input)
            input = re.sub(r'^trait', ' trait', input, flags=re.M)  # STH_main_l_english.yml
        input = re.sub(r'(?<=\w):\d+ ?(?=")', ': ', input)
        input = re.sub(r'^[ \t]+', '  ', input, flags=re.M)

        return self.yaml.load(input)

    def localized_strings(self, paths):
        """Localized strings are parsed with a standard YAML parser"""
        loc_data = { }
        for file_path in paths:
            filename = path.basename(file_path)
            print('loading {0} [{1}]'.format(filename, file_path))
            file_data = self.read_yaml_file(file_path)
            try:
                for k,v in file_data['l_english'].items():
                    loc_data[str(k)] = v
            except TypeError:
                print('Unable to find head YAML key for {}'.format(filename))
                sys.exit()
        return loc_data

    def localized_scripts(self, paths):
        """Localized scripts are parsed with a standard YAML parser"""
        loc_data = { }
        for file_path in paths:
            filename = path.basename(file_path)
            print('loading {0} [{1}]'.format(filename, file_path))
            file_data = self.read_yaml_file(file_path)
            for doc in file_data:
                print(doc)
            return file_data
            try:
                for k,v in file_data['l_english'].items():
                    loc_data[str(k)] = v
            except TypeError:
                print('Unable to find head YAML key for {}'.format(filename))
                sys.exit()
        return loc_data

    def extract_at_vars(self, entries, avlist = []):
        for e in entries:
            if list(e)[0].startswith('@'):
                at_var = list(e)[0]
                avlist[at_var] = e[at_var]
                # print(' -- ATVAR[{}] = {}'.format(at_var, e[at_var]))
        return avlist

    def replace_local_at_var(self, s):
        if s in self.local_at_vars:
            return str(self.local_at_vars[s])
        print('No match for ATVAR "{}" in {}'.format(s, repr(self.local_at_vars)))
        return s

    def normalize_data_yaml(self, contents):
        """Normalize game data files that will be loaded with the yacc based parser"""
        # New Horizons mod has their own YAML corruption
        if self.config.mod == Parser.NEW_HORIZONS:
            if "_jem'hadar" in contents:
                print(" ++ Fixing New Horizons YAML [_jem'hadar] . . .")
                contents = contents.replace("_jem'hadar", "_jem_hadar")
            if '\T' in contents:
                print(' ++ Fixing New Horizons YAML [\\T] . . .')
                contents = contents.replace('\T', "T")
            if "fed_heavy_escort_modi'in" in contents:
                print(" ++ Fixing New Horizons YAML [fed_heavy_escort_modi'in] . . .")
                contents = contents.replace("fed_heavy_escort_modi'in", "fed_heavy_escort_modi_in")
            if "class_restriction = { 0.5 }" in contents:
                print(" ++ Fixing New Horizons YAML [class_restriction = { 0.5 }] . . .")
                contents = contents.replace("class_restriction = { 0.5 }", "")
        if "event_target:" in contents:
            print(" ++ Fixing YAML [event_target:] . . .")
            contents = contents.replace("event_target:", "")
        if "33 = {" in contents:
            print(" ++ Fixing YAML [33 =] . . .")
            contents = re.sub(r'\s33 = [{]', r'ThirtyThree = {', contents)
        if '\\"' in contents:
            print(" ++ Fixing YAML [\\\"] . . .")
            contents = contents.replace('\\"', '')
        return contents

    def parse_data_dir(self, dir, doAtSubst = True):
        """Use yacc parser to read YAML data files"""
        parsed = []
        for file_path in self.get_file_paths(dir):
            print('parse {}'.format(file_path))
            contents = open(file_path).read()
            contents = self.normalize_data_yaml(contents)
            p = self.yacc_parser.parse(contents)
            if doAtSubst:
                self.local_at_vars = self.extract_at_vars(p, self.at_vars.copy())
                contents = re.sub(r'(?:[^\n\t])(@[^ \n\t]+)', lambda x: self.replace_local_at_var(x.group(1)), contents)
                try:
                    p = self.yacc_parser.parse(contents)
                except Exception as e:
                    print(contents)
                    raise
            parsed += p
        return parsed


    def __init__(self):
        self.config = Configuration()

        self.yacc_parser = STTYacc()

        self.yaml = ruamel.yaml.YAML()
        self.yaml.allow_duplicate_keys = True

        self.game_objects = {
            Parser.ARMY: { Parser.CLASS: Parser.ARMY, Parser.DIR: 'common/armies', Parser.DATA: []},
            Parser.ARMY_ATTACHMENT : { Parser.CLASS:  Parser.ARMY_ATTACHMENT, Parser.DIR: 'common/army_attachments', Parser.DATA: []},
            Parser.BUILDABLE_POP :  { Parser.CLASS: Parser.BUILDABLE_POP, Parser.DIR: 'common/buildable_pops', Parser.DATA: []},
            Parser.BUILDING :  { Parser.CLASS: Parser.BUILDING, Parser.DIR: 'common/buildings', Parser.DATA: []},
            Parser.COMPONENT :  { Parser.CLASS: Parser.COMPONENT, Parser.DIR: 'common/component_templates', Parser.DATA: []},
            Parser.EDICT :  { Parser.CLASS: Parser.EDICT, Parser.DIR: 'common/edicts', Parser.DATA: []},
            Parser.POLICY :  { Parser.CLASS: Parser.POLICY, Parser.DIR: 'common/policies', Parser.DATA: []},
            Parser.RESOURCE :  { Parser.CLASS: Parser.RESOURCE, Parser.DIR: 'common/strategic_resources', Parser.DATA: []},
            Parser.SPACEPORT_MODULE :  { Parser.CLASS: Parser.TILE_BLOCKER, Parser.DIR: 'common/spaceport_modules', Parser.DATA: []},
            Parser.TILE_BLOCKER :  { Parser.CLASS: Parser.TILE_BLOCKER, Parser.DIR: 'common/deposits', Parser.DATA: []},
            Parser.TECHNOLOGY: { Parser.CLASS: Parser.TECHNOLOGY, Parser.DIR: 'common/technology', Parser.DATA: [], Parser.SKIP_PARSE: True}
        }

        self.skip_files_that_match = ['^events?', 'tutorials?', 'pop_factions?', 'name_lists?',
                                      'messages?', 'mandates?', 'projects?', 'sections?',
                                      'triggers?', 'traits?']
        self.skip_loc_scripts_that_match = [ '_fr.txt$', '_deloc.txt$', '_frloc.txt$', '_porloc.txt$', '_ruloc_txt.txt$' ]

        self.at_vars = {}


    def run(self):
        print('Loading English localization strings . . .')
        loc_file_paths = []
        skip_re = re.compile(r'(?:{})_'.format('|'.join(self.skip_files_that_match)))
        for directory in self.config.directories:
            print('+ Loading localization strings from %s' % directory)
            loc_dir = path.join(directory, 'localisation/english')
            if not path.isdir(loc_dir):
                continue
            loc_file_paths += [path.join(loc_dir, filename) for filename
                            in listdir(loc_dir)
                            if path.isfile(path.join(loc_dir, filename))
                            and filename.endswith('l_english.yml')
                            and not skip_re.search(filename)]
        localizer = Localizer(self.localized_strings(loc_file_paths))
        localizer.put_if_not_exist('BYPASS_LGATE', 'L-Gate')   # TODO: Entry is missing from localization
        print('Finished loading English localization strings')

        print('Loading localization scripts . . .')
        loc_file_paths = []
        for directory in []: # TODO DISABLED self.config.directories:
            print('+ Loading localization scripts from %s' % directory)
            loc_dir = path.join(directory, 'common/scripted_loc')
            if not path.isdir(loc_dir):
                continue
            skip_re = re.compile(r'(?:{})_'.format('|'.join(self.skip_loc_scripts_that_match)))
            loc_file_paths += [path.join(loc_dir, filename) for filename
                            in listdir(loc_dir)
                            if path.isfile(path.join(loc_dir, filename))
                            and filename.endswith('.txt')
                            and not skip_re.search(filename)]
        print(repr(self.localized_scripts(loc_file_paths)))
        # localizer = Localizer(self.localized_scripts(loc_file_paths))
        #sys.exit()
        print('Finished loading localization scripts')

        print('Loading scripted variables . . .')
        for directory in self.config.directories:
            print('+ Loading scripted variables from %s' % directory)
            self.extract_at_vars(self.parse_data_dir(path.join(directory, 'common/scripted_variables'), False), self.at_vars)
        print('Finished scripted variables ')

        print('Loading game files . . .')
        for directory in self.config.directories:
            print('+ Loading game files from %s' % directory)
            for go in self.game_objects.values():
                go['data'] += self.parse_data_dir(path.join(directory, go[Parser.DIR]))
        print('Finished loading game files')

        icon_remaps = {}
        img_dup_filename = path.join('public', self.config.mod, 'img', 'remaps.json')
        if path.exists(img_dup_filename):
            with open(img_dup_filename, 'r') as json_file:
                icon_remaps = json.load(json_file)

        print('Processing files . . .')

        for go in self.game_objects.values():
            if Parser.SKIP_PARSE not in go or not go[Parser.SKIP_PARSE]:
                go[Parser.PARSED_DATA] = [
                    globals()[go[Parser.CLASS]](entry, localizer)
                    for entry in go[Parser.DATA]
                    if not list(entry)[0].startswith('@')
                ]

        technologies = []
        for entry in self.game_objects[Parser.TECHNOLOGY][Parser.DATA]:
            if list(entry)[0].startswith('@'):
                continue
            technologies.append(Technology(entry, icon_remaps,
                self.game_objects[Parser.ARMY][Parser.PARSED_DATA],
                self.game_objects[Parser.ARMY_ATTACHMENT][Parser.PARSED_DATA],
                self.game_objects[Parser.BUILDABLE_POP][Parser.PARSED_DATA],
                self.game_objects[Parser.BUILDING][Parser.PARSED_DATA],
                self.game_objects[Parser.COMPONENT][Parser.PARSED_DATA],
                self.game_objects[Parser.EDICT][Parser.PARSED_DATA],
                self.game_objects[Parser.POLICY][Parser.PARSED_DATA],
                self.game_objects[Parser.RESOURCE][Parser.PARSED_DATA],
                self.game_objects[Parser.SPACEPORT_MODULE][Parser.PARSED_DATA],
                self.game_objects[Parser.TILE_BLOCKER][Parser.PARSED_DATA],
                localizer, 'primitive' != self.config.mod))
        technologies.sort(key=lambda tech: {'physics': 1, 'society': 2, 'engineering': 3}[tech.area] * 100 + tech.tier)

        filename = path.join('public', self.config.mod, 'techs.json')
        with open(filename, 'w') as outfile:
            json.dump(technologies, outfile, indent=2, separators=(',', ': '),
                cls=TechnologyJSONEncoder, sort_keys=True)

        print('Wrote {} techs to {}'.format(len(technologies), filename))


if __name__ == '__main__':
    Parser().run()