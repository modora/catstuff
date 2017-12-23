import yaml
import configparser
import collections

import catstuff.tools

class ConfigError(Exception):
    pass


class Config:
    def __init__(self, config: dict):
        self._config = config

    def __getitem__(self, item):
        return self.config[item]

    @property
    def config(self):
        return self._config

    @classmethod
    def load_config(cls, path):
        from catstuff.tools import path as path_

        conf = cls(import_yaml(path_.expandpath(path)))
        return conf

    def get(self, keys: list, default=None):
        """ Get the value of some key in the config"""
        conf = self.config.copy()
        """ Walk into config"""
        for key in keys:
            try:
                conf = conf[key]  # update subconfig
            except (KeyError, TypeError):
                return default
        return conf


class ConfigGroup:
    # This is a placeholder object for when groups are supported
    def __init__(self):
        self.configs = collections.OrderedDict()

    def set_config(self, name: str, config: Config):
        self.configs.update({name: config})

    def delete_config(self, name: str):
        try:
            del self.configs[name]
        except KeyError:
            pass

    def get_config(self, name, **kwargs):
        try:
            return self.configs[name]
        except KeyError as e:
            try:
                return kwargs['default']
            except KeyError:
                return e

    def get(self, keys: list, **kwargs):
        for config in self.configs:  # prioritizes the oldest configs
            try:
                return config.get(keys)
            except KeyError:
                pass
        try:
            return kwargs['default']
        except KeyError:
            raise KeyError('{keys} key not found in any configs'.format(keys=keys))


class PluginConfig:
    """ Convenience parser for plugin configs"""
    def __init__(self, config: dict):
        self._config = config

    def __getitem__(self, item):
        return self.get(item)

    @property
    def config(self):
        return self._config

    @classmethod
    def from_yapsy(cls, yapsy_obj):
        """ Initilalize using a yapsy loaded plugin"""
        config = {}
        for section in yapsy_obj.details.sections():
            for option in yapsy_obj.details.options(section):
                try:  # attempt to init option
                    config[section][option] = None
                except KeyError:  # occurs if section not inited yet
                    config[section] = {}
                config[section][option] = yapsy_obj.details.get(section, option)
        return cls(config)

    @classmethod
    def from_path(cls, path):
        """ Initilize using the path to config"""
        config = cls(import_ini(path))
        config.path = path
        return config

    def get_section(self, section) -> dict:
        """ Returns all options for some section of a config"""
        try:
            return self.config[section]
        except KeyError:
            raise configparser.NoSectionError

    def get(self, option: str, section=None, **kwargs):
        """
        Gets the value of an option
        :param option: Name of option (option name is case-insensitive)
        :param section: (default=None)  Sections to look though. If None is specified, then search through all sections
        :param kwargs: return value if option not found; must be entered using named parameter
        :return:
        :raise: KeyError: if option not found
        """

        if section is not None:
            try:
                return self.config[section][option]
            except KeyError as e:
                try:
                    return kwargs['default']
                except KeyError:
                    raise e
        else:  # look through all sections
            for section in self.config:
                try:
                    return self.config[section][option]
                except KeyError:
                    pass
            try:
                return kwargs['default']
            except KeyError:
                raise KeyError('Option [} not found in any section of config'.format(option))


def import_ini(path: str) -> dict:
    """
    Reads an ini config file and returns it as a dict
    :param path:
    :return:

    Example:
    sample.plugin

    [Core]
    Name = Hello World

    [Documentation]
    Version = 1.0

    >>> import_ini("sample.plugin")
    {'Core': {'name': 'Hello World'}, 'Documentation': {'version': '1.0'}}

    """
    config = configparser.ConfigParser()
    config.read(path)

    d = collections.defaultdict(dict)
    for section in config.sections():
        for option in config.options(section):
            d[section][option] = config.get(section, option)
    return dict(d)


def import_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        d = yaml.load(f)
    return {} if d is None else d


class YamlExplicitDumper(yaml.SafeDumper):
    """
    A dumper that will never emit aliases. -- Found from pyyaml ticket #91
    Usage: yaml.dump(..., Dumper=ExplicitDumper)
    """
    def ignore_aliases(self, data):
        return True
