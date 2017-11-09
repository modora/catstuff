"""
This is the global config file
"""
import os

_dir = os.path.dirname(os.path.realpath(__file__))

config_struct = {
    'db': {
        'host': {
            'type': [str],
        },
        'name': {
            'type': [str]
        },
        'port': {
            'type': [int]
        }
    },
    'groups': {
        'type': [dict]
    },
    'import': {
        'type': [list]
    },
    'modules': {
        'type': [dict]
    },
    'resources': {
        'max_memory': {
            'type': [int]
        },
        'max_threads': {
            'type': [int]
        },
    },
    'tasks': {
        'type': [list]
    },
    'version': {
        'type': [str]
    }
}


import catstuff.tools.common
import catstuff.tools.config
import yaml

default_config_path = r'default.yml'
sample_config_path = r'sample.yml'

default_conf = catstuff.tools.config.load_config(default_config_path)
conf = catstuff.tools.config.load_config(sample_config_path)

catstuff.tools.common.title('Config struct')
print(yaml.dump(config_struct))
catstuff.tools.common.title('Default')
print(yaml.dump(default_conf))
catstuff.tools.common.title('Sample')
print(yaml.dump(conf))
catstuff.tools.common.title('Parsed')
print(NotImplementedError)

catstuff.tools.common.title('Get leaves')
conf_leaves = catstuff.tools.config.get_leaves(default_conf)
print("Set:", conf_leaves)
print("List:", [catstuff.tools.config.dot_to_list(leaf) for leaf in conf_leaves])
print("List -> Set:", {catstuff.tools.config.list_to_dot(catstuff.tools.config.dot_to_list(leaf)) for leaf in conf_leaves})
print(list(conf_leaves)[0], ":", catstuff.tools.config.eval_conf(default_conf, list(conf_leaves)[0]))

catstuff.tools.common.title('Sample Groups')
groups = catstuff.tools.config.get_groups(conf)
print("Set:", groups)
print("List:", [catstuff.tools.config.group_dot_to_list(group) for group in groups])
print("List -> Set:", {catstuff.tools.config.group_list_to_dot(catstuff.tools.config.group_dot_to_list(group)) for group in groups})
print(list(groups)[0], ":", catstuff.tools.config.eval_conf(conf, list(groups)[0], leaf_type='group'))

