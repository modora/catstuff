import yapsy.PluginManager
import catstuff.tools.plugins
import os

_dir = os.path.dirname(os.path.realpath(__file__))
plugin_places = [os.path.join(_dir, path) for path in {'.', '../plugins'}]

manager = yapsy.PluginManager.PluginManager()
manager.setPluginInfoExtension('plugin')
manager.setPluginPlaces(plugin_places)
manager.setCategoriesFilter({
    'Tasks': catstuff.tools.plugins.CSTask,
    'Actions': catstuff.tools.plugins.CSAction
})

manager.collectPlugins()