import yapsy.PluginManager
import os
import catstuff.tools.plugins

_dir = os.path.dirname(os.path.realpath(__file__))

manager = yapsy.PluginManager.PluginManager()
manager.setPluginPlaces([
    os.path.join(_dir, "../../plugins")
])
manager.setCategoriesFilter({
    "Plugins": catstuff.tools.plugins.CSTask
})
manager.setPluginInfoExtension('plugin')