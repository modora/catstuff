import yaml


def load_config(path):
    try:
        return yaml.load(open(path, 'r'))
    except yaml.YAMLError as e:
        print("Error trying to load {path}: {error}".format(path=path, error=e))


def dot_to_list(dot_str: str):
    """ Converts from dot-notation to a list"""
    return dot_str.split('.')


def group_dot_to_list(dot_str: str):
    """ Converts from group, dot-notation to a list"""
    lst = []
    for group in dot_str.split('.'):
        lst.append('groups')
        lst.append(group)
    return lst


def list_to_dot(dot_list: (list, tuple)):
    """ Converts a list of strings to dot notation. All dots are replaced with underscores"""
    assert all(isinstance(e, str) for e in dot_list), "All elements in list must be strings"
    string = ''
    for ele in dot_list:
        s = ele.replace('.', '_')
        if string == '':
            string = s
        else:
            string += '.' + s
    return string


def group_list_to_dot(dot_list: (list, tuple)):
    """ Converts a list of strings to dot notation. All dots are replaced with underscores"""
    assert all(isinstance(e, str) for e in dot_list), "All elements in list must be strings"
    string = ''
    for i, ele in enumerate(dot_list):
        # lists are written as ['groups', 'NAME', 'groups', 'NAME', ...]
        # Use enumeration in case 'NAME' == 'groups'
        # if ele == 'groups' will accidentally skip the 'NAME'
        if i % 2 == 0:  # skip the 'groups' elements
            continue
        s = ele.replace('.', '_')
        if string == '':
            string = s
        else:
            string += '.' + s
    return string


def get_leaves(config: dict):
    """
    Returns all the leaves in some json-styled config

    WARNING: All keys with a dot ('.') in their name are replaced with underscores ('_')
    :param config: json config
    :return: set in dot-notation
    """
    def walk(config: dict, node: (str, type(None))):
        for key in config:
            if isinstance(config[key], dict):
                k = key.replace('.', '_')
                n = '.'.join([node, k]) if node not in {'', None} else k
                walk(config[key], node=n)
            else:
                k = key.replace('.', '_')
                leaf = '.'.join([node, k]) if node not in {'', None} else k
                leaves.add(leaf)
    leaves = set()
    walk(config, node=None)
    return leaves


def get_groups(config: dict):
    """ Gets a list of all groups and subgroups in dot notation"""
    def walk(config: dict, node: (str, None)):
        for g in set(config.get('groups', {}).keys()):
            group = g.replace('.', '_')
            n = '.'.join([node, group]) if node not in ('', None) else group
            groups.add(n)
            walk(config['groups'][g], node=n)

    groups = set()
    walk(config, node=None)
    return groups


def get_modules(config: dict):
    return set(config.get('modules', {}).keys())


def eval_conf(config: dict, leaf: str, leaf_type=None):
    keys = {
        None: dot_to_list,
        'group': group_dot_to_list
    }[leaf_type](leaf)
    conf = config.copy()
    for key in keys:
        conf = conf[key]
    return conf

# import os
# import fnmatch
# import yaml
# from . import dicts
# from .common import expandpath
#
#
# def get_groups(config):
#     # Returns a list of the groups within the config
#     groups = []
#
#     def recursive_get_group(config, prefix=''):
#         for group in config.get('groups', {}):
#             if prefix is '':
#                 groups.append(group)
#             else:
#                 groups.append('.'.join((prefix, group)))
#             recursive_get_group(config['groups'][group], prefix=groups[-1])
#
#     recursive_get_group(config)
#     return groups
#
#
# def get_group_config(config, group):
#     '''
#     Returns the config of a config for a given group
#     :param config: dict
#     :param group: the group within the config in dot notation (group.subgroup.subsubgroup)
#     :return: config
#     '''
#     if group == '':
#         return config
#     levels = dot_to_list(group)
#     while levels:
#         level = levels.pop(0)
#         if level not in config['groups']:
#             raise KeyError('Nonexistent group: {group}'.format(group=group))
#         config = config['groups'][level]
#     return config
#
#
# def load_config(path):
#     try:
#         return yaml.load(open(path, 'r'))
#     except yaml.YAMLError as e:
#         print("Error trying to load {path}: {error}".format(path=path, error=e))
#
#
# # def build(config):
# #     ''' Parses a raw config and import other files'''
# #     import_list = config['top']['import']
#
#
# def recursive_config(config, func, *args, **kwargs):
#     '''
#     Applies the function to each level of the config
#     :param config: config file
#     :param func: function to recursively apply
#     :param args: function arguments
#     :param kwargs: function kwargs
#     :return:
#     '''
#     for group in config.get('groups', {})
#
#
# def import_path_list(path, include=('*',), exclude=(), max_depth=0, follow_links=False, default_action=False):
#     '''
#     Returns the list of files to import for a given path
#     :param path: import path
#     :param include: iterable pattern of paths to include (supports globbing)
#     :param exclude: iterable pattern of paths to exclude (supports globbing)
#     :param max_depth: maximum search depth if path is a directory
#     :param follow_links: follow symlinks if path is a directory
#     :param default_action: if not in include nor exclude
#     :return:
#
#     Files are imported if both the include and exclude pattern cases are satisfied
#     Otherwise, fallback to the default_action
#     '''
#     supported_ext = ('.yaml', '.yml', '.json')
#
#     if max_depth == -1:
#         # close enough to infinity!!
#         # This is more as a safety mechanism to prevent searching a super-nested
#         # directory tree
#         max_depth = 64
#
#     def path_filter(path):
#         '''
#         Returns a boolean value whether the path should be imported
#         :param path: full path
#         :return: bool
#
#         Precedence
#             exclude > include > default_action
#         '''
#         for exc in exclude:
#             if fnmatch.fnmatchcase(os.path.basename(path), exc):
#                 return False
#         for inc in include:
#             if fnmatch.fnmatchcase(os.path.basename(path), inc):
#                 return True
#         return default_action
#
#     def file_filter(path):
#         def ext_filter(path):
#             return True if os.path.splitext(path)[1] in supported_ext else False
#
#         result = [
#             path_filter(path),
#             ext_filter(path)
#         ]
#         return all(result)
#
#     # Get the list of files to import
#     if not os.path.isabs(path):
#         raise os.error('Import path must be absolute')
#     path = expandpath(path)
#     imported_files = []
#     if os.path.isfile(path):
#         imported_files.append(path) if file_filter(path) else None
#     else:  # isdir
#         depth_offset = path.rstrip(os.path.sep).count(os.path.sep)
#         for root, dirs, files in os.walk(path, followlinks=follow_links):
#             depth = root.rstrip(os.path.sep).count(os.path.sep) - depth_offset
#             if depth == max_depth:
#                 del dirs[:]
#             for i, dir in enumerate(dirs):
#                 if not path_filter(dir):
#                     del dirs[i]
#             for file in files:
#                 f = os.path.join(root, file)
#                 imported_files.append(f) if file_filter(f) else None
#     return imported_files
#
#
# def import_config(import_list, config=None):
#     if config is None:
#         config = {}
#     for path in import_list:
#         config = dicts.merge(config, load_config(path), recursive=True)
#     return config
