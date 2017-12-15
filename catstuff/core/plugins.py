from yapsy.PluginManager import PluginManager
import os

_dir = os.path.dirname(os.path.realpath(__file__))

__version__ = '1.3'


class StrMethod(str):
    """ Base class for StrMethod plugin category"""
    '''
    To avoid collisions with other plugins, use the python name mangling '__attr' 
    with double underscores for private variables. Additionally, name your subclass
    the name of your plugin (underscore separated)
    '''

    pass


class _CSPluginBase:
    """ Template for most catstuff plugin classes"""
    def __init__(self, name):
        self.name = name

    def main(self, *args, **kwargs):
        print("Executed main method of '{name}' plugin of class '{cls}'".format(
            name=self.name, cls=self.__class__.__name__))


class CSAction(_CSPluginBase):
    """ Base class for a catstuff action"""
    def __init__(self, name):
        super().__init__(name)

    def main(self, *args):
        super().main()


class CSTask(_CSPluginBase):
    """ Base class for a catstuff task"""
    def __init__(self, name, build):
        super().__init__(name)
        self.build = build


class CSPluginManager(PluginManager):
    __version__ = __version__
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
