from os import makedirs, path

import importlib.util
import argparse
import re
import sys

class Configuration:
    def valid_label(self, label):
        if not re.match(r'^\w+$', label):
            raise argparse.ArgumentTypeError('Must match [a-z0-9_]')
        elif label not in self.config.mods.keys():
            raise argparse.ArgumentTypeError('Unsupported mod')
        elif not path.isdir(path.join('public', label)):
            makedirs(path.join('public', label))
        return label.lower()

    def __init__(self):
        spec = importlib.util.spec_from_file_location('config', './config.py')
        self.config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.config)

        arg_parser = argparse.ArgumentParser(description='Parse Stellaris tech and localization files')
        arg_parser.add_argument('mod', type=self.valid_label, default='vanilla', nargs='?', help='Use configuration for loadable game mod <mod>')

        args = arg_parser.parse_args()
        mod_id = self.config.mods[args.mod]
        self.mod = args.mod

        self.directories = [self.config.game_dir]
        if type(mod_id) is int:
            mod_dir = path.join(self.config.workshop_dir, str(mod_id), 'mod')
            self.directories.append(mod_dir)
