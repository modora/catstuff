from catstuff.tools.db import property_getter, Collection
import catstuff.core


class StrMethod(str):
    """ Base method to add to the CSStr class"""
    '''
    To avoid collisions with other plugins, use the python name mangling '__attr' 
    with double underscores for private variables. Additionally, name your subclass
    the name of your plugin (underscore separated)
    '''

    pass


class _CSPluginTemplate:
    """ Template for most catstuff plugin classes"""
    def __init__(self, name):
        super().__init__()
        self.name = name

    def main(self, *args, **kwargs):
        print("Executed main method of '{name}' plugin of class '{cls}'".format(
            name=self.name, cls=self.__class__.__name__))


class CSAction(_CSPluginTemplate):
    """ Create a catstuff action"""
    def __init__(self, name):
        super().__init__(name)

    def main(self, *args):
        super().main()


class CSTask(_CSPluginTemplate):
    """ Create a catstuff task"""
    def __init__(self, name, build):
        super().__init__(name)
        self.build = build

    @property
    def config(self):
        return property_getter(self, "_config", default={})

    @property
    def output(self):
        return property_getter(self, "_output", default={})
