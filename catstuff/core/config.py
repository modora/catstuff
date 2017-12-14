import yaml
import collections
import catstuff.tools as tools


class Config:
    default_path = '~/.conf/catstuff.yml'
    def __init__(self, config: dict):
        self._config = config

    def __getitem__(self, item):
        return self.config[item]

    @property
    def config(self):
        return self._config

    @classmethod
    def load_config(cls, path):
        conf = cls(load_yaml(path))
        return conf

    @classmethod
    def load_default(cls):
        return cls.load_config(tools.path.expandpath(cls.default_path))

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
    # TODO: This is a placeholder object for when groups are supported
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
            return  kwargs['default']
        except KeyError:
            raise KeyError('{keys} key not found in any configs'.format(keys=keys))


def load_yaml(path):
    with open(path, 'r') as f:
        d = yaml.load(f)
    return {} if d is None else d