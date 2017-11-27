from yapsy.PluginManager import PluginManager
import catstuff.tools.plugins
import os

_dir = os.path.dirname(os.path.realpath(__file__))


class CSPluginManager(PluginManager):
    categories = {
        'Task': catstuff.tools.plugins.CSTask,
        'Action': catstuff.tools.plugins.CSAction,
        'StrMethod': catstuff.tools.plugins.StrMethod
    }

    extensions = 'plugin'
    plugin_places = [os.path.join(_dir, path) for path in {'.', '../plugins'}]

    def __init__(self):
        super().__init__(
            categories_filter=self.categories,
            directories_list=self.plugin_places,
            plugin_info_ext=self.extensions
        )
        self.collectPlugins()