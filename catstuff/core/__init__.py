from . import dbs
from . import plugins
from . import str_formatter
from . import vars
from . import config


def init(config_path: str=None):
    """ Initializes the catstuff environment"""
    from catstuff import tools

    def init_config():
        if config_path is None:
            try:
                return config.CSConfig.load_default()
            except FileNotFoundError:
                tools.path.touch(config.CSConfig.default_path)
                return config.CSConfig.load_default()
        else:
            return config.CSConfig.load_config(config_path)

    data = {
        'config': init_config()
    }
    vars.CSVarPool.setup(data, app='catstuff')
    vars.CSVarPool.setup()