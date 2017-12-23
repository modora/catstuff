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

    def init_CSStr(config: config.CSConfig):
        remap = config.get(['CSStr'], default={})
        return str_formatter.CSStrConstructor(remap)


    vars_ = vars.CSVarPool(app='catstuff')
    conf = init_config()
    vars_['config'] = conf
    vars_['manager'] = plugins.CSPluginManager()
    vars_['CSStr'] = init_CSStr(conf)
