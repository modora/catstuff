import yaml
import configparser
import collections


class ConfigError(Exception):
    pass


class PluginConfig:
    def __init__(self, config: dict):
        self._config = config

    @property
    def config(self):
        return self._config

    @classmethod
    def from_yapsy(cls, yapsy_obj):
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
        config = cls(import_ini(path))
        config.path = path
        return config

    def get_section(self, section):
        try:
            self.config[section]
        except KeyError:
            raise configparser.NoSectionError

    def get(self, option: str, section=None, **default):
        """
        Gets the value of an option
        :param option: Name of option (option name is case-insensitive)
        :param section: (default=None)  Sections to look though. If None is specified, then search through all sections
        :param default: return value if option not found; must be entered using named parameter
        :return:
        :raise: KeyError: if option not found
        """
        if section is not None:
            return try_get(self.config, [section, option], **default)
        else:  # look through all sections
            for section in self.config:
                try:
                    return try_get(self.config[section], option)
                except KeyError:
                    pass
            return default['default']


def import_ini(path):
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
    {'Core': {'Name': 'Hello World'}, 'Documentation': {'Version': '1.0'}}

    """
    config = configparser.ConfigParser()
    config.read(path)

    d = {}
    for section in config.sections():
        d[section] = {}
        for option in config.options(section):
            d[section][option] = config.get(section, option)
    return d


def load_yaml(path):
    try:
        return yaml.load(open(path, 'r'))
    except yaml.YAMLError as e:
        print("Error trying to load {path}: {error}".format(path=path, error=e))


def try_get(config: dict, keys: (list, str), **default):
    """
    Evaluates the value of some key or nested key in a config
    :param config: Config file
    :param keys:
    :type str or list
    :param default: return value if key not found
    :return:
    """

    # Using **default to emulate a function overload so that if the default keyword
    # is not specified in the input, an exception is raised

    if isinstance(keys, str):
        keys = {keys}
    conf = config.copy()
    for key in keys:
        try:
            conf = conf[key]
        except KeyError as e:
            try:
                return default['default']
            except KeyError:
                raise e
    return conf


class ConfigGroup:
    def __init__(self):
        self.group = collections.OrderedDict()

    def set_config(self, name: str, config: dict):
        self.group.update({name: config})

    def delete_config(self, name: str):
        try:
            del self.group[name]
        except KeyError:
            pass

    def get_config(self, name, **kwargs):
        return try_get(self.group, name, **kwargs)

    def get(self, keys, **default):
        for config in self.group:  # prioritizes the oldest configs
            try:
                return try_get(config, keys)
            except KeyError:
                pass
        return default['default']


class ExplicitDumper(yaml.SafeDumper):
    """
    A dumper that will never emit aliases. -- Found from pyyaml ticket #91
    Usage: yaml.dump(..., Dumper=ExplicitDumper)
    """
    def ignore_aliases(self, data):
        return True
