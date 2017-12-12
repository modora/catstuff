from yapsy.PluginManager import PluginManager
from catstuff.core.plugin_categories import CSTask, CSAction, StrMethod
import os

_dir = os.path.dirname(os.path.realpath(__file__))

__version__ = '1.2'


class CSPluginManager(PluginManager):
    categories = {
        'Task': CSTask,
        'Action': CSAction,
        'StrMethod': StrMethod
    }

    extensions = 'plugin'
    plugin_places = [os.path.join(_dir, path) for path in {'../core_plugins', '../plugins'}]

    def __init__(self):
        super().__init__(
            categories_filter=self.categories,
            directories_list=self.plugin_places,
            plugin_info_ext=self.extensions
        )
        self.collectPlugins()


class MissingPluginException(Exception):
    pass
