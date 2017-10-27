import yaml
import os
import catstuff.tools.config as config
import catstuff.tools.dicts as dicts
from catstuff.tools.common import expandpath

__dir__ = os.path.dirname(expandpath(__file__))


class Config:
    supported_ext = ('.yml', '.yaml', '.json')
    default_config_path = os.path.join(__dir__, 'default.yml')
    config_version = '1.0'

    def __init__(self, path=None):
        self.paths = [self.default_config_path]
        self.raw_config = self.load(self.default_config_path)

        self.version = self.raw_config.get(self.config_version)

        self.config = self.raw_config  # init
        self.groups = self.get_groups()

        self.imported = set()  # used mostly for debugging, this tells nothing about the group inserted into

        # if path is not None:
        #     self.import_config(path)



    def get_groups(self):
        ''' Returns a list of the groups within the config'''
        return config.get_groups(self.config)


    def get_group_config(self, group):
        return config.get_group_config(self.config, group)

    @staticmethod
    def load(path):
        return config.load_config(expandpath(path))

    def raw_dump(self, **kwargs):
        defaults = {
            'indent': 2,
            'Dumper': ExplicitDumper
        }
        yaml_kwargs = {**defaults, **kwargs}
        return yaml.dump(self.raw_config, **yaml_kwargs)

    def build(self, path,
                      include=('*',), exclude=(), max_depth=0, follow_links=False, default_action=False):
        # top level import
        import_list = config.get_import_list(path, include=include, exclude=exclude, max_depth=max_depth,
                                             follow_links=follow_links, default_action=default_action)
        conf = self.raw_config


        while import_list:
            config.import_config()

        self.imported.union(set(config.get_import_list(path,include=include, exclude=exclude, max_depth=max_depth,
                                                       follow_links=follow_links, default_action=default_action)))
        self.config

    # def import_config(self, path, level='top'):
    #     '''Adds the path to the top level import'''
    #     self.raw_config['top']['import'].append(path)

    # def import_config(self, path, depth=-1):
    #     path = expandpath(path)
    #     for p in glob.glob(path):
    #         print(p)
    #         if os.path.splitext(p)[1] in self.supported_ext:
    #             print('is file')
    #             self.paths.append(path)
    #             self.config = merge(self.config, self.load(path))
    #         else:
    #             print('is dir')