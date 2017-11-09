import yaml
import os
import catstuff.tools.config
import catstuff.tools.dicts

_dir = os.path.dirname(os.path.realpath(__file__))


def import_config(path):
    try:
        return yaml.load(open(path, 'r'))
    except yaml.YAMLError as e:
        print("Error trying to load {path}: {error}".format(path=path, error=e))

class Leaves:
    def __init__(self):
        self.leaves = {}

    @staticmethod
    def _convert_leaf(leaf: (list, str), type):
        if isinstance(leaf, list):
            return leaf  # list mode is always explicit
        elif isinstance(leaf, str):
            return {
                None: lambda leaf: catstuff.tools.config.dot_to_list(leaf),
                'group': lambda leaf: catstuff.tools.config.group_dot_to_list(leaf),
            }[type](leaf)

    def _leaf_to_str(self, leaf, leaf_type=None) -> str:
        return catstuff.tools.config.list_to_dot(self._convert_leaf(leaf, leaf_type)

    def add(self, leaf: (str, list), leaf_type=None, **kwargs):
        properties = {
            'value': kwargs.get('value'),
            'default': kwargs.get('default'),
        }

        leaf = self._leaf_to_str(leaf, leaf_type=leaf_type)

        self.leaves.update({leaf: properties})

    def delete(self, leaf: (str, list), leaf_type=None):
        leaf = self._leaf_to_str(leaf, leaf_type=leaf_type)
        del self.leaves[leaf]

    def get(self, leaf, leaf_type=None, property='value', default=None):
        leaf = self._leaf_to_str(leaf, leaf_type=leaf_type)
        try:
            return self.leaves[leaf][property]
        except KeyError:
            return default

class Config:
    supported_ext = {'.yml', '.yaml', '.json'}
    special_keys = {'groups', 'modules'}
    default_config_path = os.path.join(_dir, 'default.yml')
    config_version = '1.0'  # current config version

    def __init__(self):
        self.config = {}
        self.CS_settings = {}
        self.module_settings = {}
        self.groups = set()

    def build(self):
        self.groups = catstuff.tools.config.get_groups(self.config)
        self.module_settings = self.get('modules')
        self.CS_settings = self.config.copy()
        for key in self.special_keys:
            try:
                del self.CS_settings[key]
            except KeyError:
                pass

    @staticmethod
    def _convert_leaf(leaf: (list, str), type):
        if isinstance(leaf, list):
            return leaf  # list mode is always explicit
        elif isinstance(leaf, str):
            return {
                None   : lambda leaf: catstuff.tools.config.dot_to_list(leaf),
                'group': lambda leaf: catstuff.tools.config.group_dot_to_list(leaf),
            }[type](leaf)

    def get(self, leaf, leaf_type=None, default=None):
        leaf = self._convert_leaf(leaf, leaf_type)

        try:
            value = self.config.copy()
            for key in leaf:
                value = value[key]
            return value
        except KeyError:
            return default


# class Config:
#     supported_ext = ('.yml', '.yaml', '.json')
#     default_config_path = os.path.join(__dir__, 'default.yml')
#     config_version = '1.0'
#
#     def __init__(self, path=None):
#         self.paths = [self.default_config_path]
#         self.raw_config = self.load(self.default_config_path)
#
#         self.version = self.raw_config.get(self.config_version)
#
#         self.config = self.raw_config  # init
#         self.groups = self.get_groups()
#
#         self.imported = set()  # used mostly for debugging, this tells nothing about the group inserted into
#
#         # if path is not None:
#         #     self.import_config(path)
#
#
#
#     def get_groups(self):
#         ''' Returns a list of the groups within the config'''
#         return config.get_groups(self.config)
#
#
#     def get_group_config(self, group):
#         return config.get_group_config(self.config, group)
#
#     @staticmethod
#     def load(path):
#         return config.load_config(expandpath(path))
#
#     def raw_dump(self, **kwargs):
#         defaults = {
#             'indent': 2,
#             'Dumper': ExplicitDumper
#         }
#         yaml_kwargs = {**defaults, **kwargs}
#         return yaml.dump(self.raw_config, **yaml_kwargs)
#
#     def build(self, path,
#                       include=('*',), exclude=(), max_depth=0, follow_links=False, default_action=False):
#         # top level import
#         import_list = config.get_import_list(path, include=include, exclude=exclude, max_depth=max_depth,
#                                              follow_links=follow_links, default_action=default_action)
#         conf = self.raw_config
#
#
#         while import_list:
#             config.import_config()
#
#         self.imported.union(set(config.get_import_list(path,include=include, exclude=exclude, max_depth=max_depth,
#                                                        follow_links=follow_links, default_action=default_action)))
#         self.config
#
#     # def import_config(self, path, level='top'):
#     #     '''Adds the path to the top level import'''
#     #     self.raw_config['top']['import'].append(path)
#
#     # def import_config(self, path, depth=-1):
#     #     path = expandpath(path)
#     #     for p in glob.glob(path):
#     #         print(p)
#     #         if os.path.splitext(p)[1] in self.supported_ext:
#     #             print('is file')
#     #             self.paths.append(path)
#     #             self.config = merge(self.config, self.load(path))
#     #         else:
#     #             print('is dir')