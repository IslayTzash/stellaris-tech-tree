#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import json
import re
import ruamel.yaml as yaml
import sys

from configuration import Configuration
from game_objects import Army, ArmyAttachment, BuildablePop, Building, \
    Component, Edict, Localizer, Policy, Resource, SpaceportModule, Technology, \
    TechnologyJSONEncoder, TileBlocker
from os import listdir, path
from yacc import STTYacc

class Parser:

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


    def localized_strings(self, paths):
        loc_data = { }
        for file_path in paths:
            filename = path.basename(file_path)
            print('loading {}'.format(filename))

            # Coerce Paradox's bastardized YAML into compliance
            not_yaml_lines = codecs.open(file_path, 'r', 'utf-8-sig').readlines()
            not_yaml = ''
            for line in not_yaml_lines:
                quote_instances = [i for i, char in enumerate(line) if char == '"']
                if len(quote_instances) >= 2:
                    # Some lines have invalid data after terminal quote:
                    last = quote_instances[-1]
                    line = line[:last + 1] + '\n'
                    if len(quote_instances) > 2:
                        second = quote_instances[1]
                        line = (line[0:second]
                            + line[second:last].replace('"', r'\"')
                            + line[last:])
                not_yaml += line

            # still_not_yaml = re.sub(r'£\w+  |§[A-Z!]', '', not_yaml)
            still_not_yaml = not_yaml
            resembles_yaml = re.sub(r'(?<=\w):\d+ ?(?=")', ': ', still_not_yaml)
            actual_yaml = re.sub(r'^[ \t]+', '  ', resembles_yaml, flags=re.M)

            file_data = yaml.load(actual_yaml, Loader=yaml.Loader)
            loc_map = file_data['l_english']
            try:
                loc_data.update(loc_map)
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
        # s = s.strip()
        if s in self.local_at_vars:
            print('replacint "{}" with {}'.format(s, str(self.local_at_vars[s])))
            return str(self.local_at_vars[s])
        print('No match for "{}" in {}'.format(s, '')) # repr(self.local_at_vars)))
        return s

    def parse_data_dir(self, dir, doAtSubst = True):
        parsed = []
        for file_path in self.get_file_paths(dir):
            print('parse {}'.format(file_path))
            contents = open(file_path).read()
            # New Horizons mod has their own YAML corruption
            if self.config.mod == 'new_horizon' and "jem'hadar" in contents:
                print('fixing New Horizons YAML ...')
                contents = contents.replace("_jem'hadar", "_jem_hadar")
            if "event_target:" in contents:
                contents = contents.replace("event_target:", "")
            if "33 = {" in contents:
                contents = contents.replace("33 = {", "ThirtyThree = {")
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

        self.game_objects = {
            'Army': { 'class': 'Army', 'dir': 'common/armies', 'data': []},
            'ArmyAttachment' : { 'class': 'ArmyAttachment', 'dir': 'common/army_attachments', 'data': []},
            'BuildablePop' :  { 'class': 'BuildablePop', 'dir': 'common/buildable_pops', 'data': []},
            'Building' :  { 'class': 'Building', 'dir': 'common/buildings', 'data': []},
            'Component' :  { 'class': 'Component', 'dir': 'common/component_templates', 'data': []},
            'Edict' :  { 'class': 'Edict', 'dir': 'common/edicts', 'data': []},
            'Policy' :  { 'class': 'Policy', 'dir': 'common/policies', 'data': []},
            'Resource' :  { 'class': 'Resource', 'dir': 'common/strategic_resources', 'data': []},
            'SpaceportModule' :  { 'class': 'SpaceportModule', 'dir': 'common/spaceport_modules', 'data': []},
            'TileBlocker' :  { 'class': 'TileBlocker', 'dir': 'common/deposits', 'data': []},
            'Technology': { 'class': 'Technology', 'dir': 'common/technology', 'data': [], 'skipParse': True}
        }

        skip_terms = ['^events?', 'tutorials?', 'pop_factions?', 'name_lists?',
                    'messages?', 'mandates?', 'projects?', 'sections?',
                    'triggers?', 'traits?']
        self.has_skip_term = re.compile(r'(?:{})_'.format('|'.join(skip_terms)))

        self.at_vars = {}


    def run(self):
        print('Loading localization strings . . .')
        loc_file_paths = []
        for directory in self.config.directories:
            loc_dir = path.join(directory, 'localisation/english')
            loc_file_paths += [path.join(loc_dir, filename) for filename
                            in listdir(loc_dir)
                            if path.isfile(path.join(loc_dir, filename))
                            and filename.endswith('l_english.yml')
                            and not self.has_skip_term.search(filename)]
        localizer = Localizer(self.localized_strings(loc_file_paths))
        localizer.put_if_not_exist('BYPASS_LGATE', 'L-Gate')   # TODO: Entry is missing from localization
        print('Finished loading localization strings')

        print('Loading scripted variables . . .')
        for directory in self.config.directories:
            self.extract_at_vars(self.parse_data_dir(path.join(directory, 'common/scripted_variables'), False), self.at_vars)
        print('Finished scripted variables ')

        print('Loading game files . . .')
        for directory in self.config.directories:
            for go in self.game_objects.values():
                go['data'] += self.parse_data_dir(path.join(directory, go['dir']))
        print('Finished loading game files')

        print('Processing files . . .')

        for go in self.game_objects.values():
            if 'skipParse' not in go or not go['skipParse']:
                go['parsed_data'] = [
                    globals()[go['class']](entry, localizer)
                    for entry in go['data']
                    if not list(entry)[0].startswith('@')
                ]

        technologies = []
        for entry in self.game_objects['Technology']['data']:
            if list(entry)[0].startswith('@'):
                continue
            technologies.append(Technology(entry,
                self.game_objects['Army']['parsed_data'], self.game_objects['ArmyAttachment']['parsed_data'],
                self.game_objects['BuildablePop']['parsed_data'], self.game_objects['Building']['parsed_data'],
                self.game_objects['Component']['parsed_data'], self.game_objects['Edict']['parsed_data'],
                self.game_objects['Policy']['parsed_data'], self.game_objects['Resource']['parsed_data'],
                self.game_objects['SpaceportModule']['parsed_data'], self.game_objects['TileBlocker']['parsed_data'],
                localizer, 'primitive' != self.config.mod))
        technologies.sort(key=lambda tech: {'physics': 1, 'society': 2, 'engineering': 3}[tech.area] * 100 + tech.tier)

        filename = path.join('public', self.config.mod, 'techs.json')
        with open(filename, 'w') as outfile:
            json.dump(technologies, outfile, indent=2, separators=(',', ': '),
                cls=TechnologyJSONEncoder, sort_keys=True)

        print('Wrote {} techs to {}'.format(len(technologies), filename))


if __name__ == '__main__':
    Parser().run()