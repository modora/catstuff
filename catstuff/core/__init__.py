from . import dbs
from . import plugins
from . import str_formatter
from . import vars
from . import config
from . import checkpoint


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

    vars_ = vars.CSVarPool(app='catstuff')
    vars_.set('config', init_config())
    vars_.set('manager', plugins.CSPluginManager())
