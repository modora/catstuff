from yapsy.PluginManager import PluginManager
import catstuff.toolbox.modules as mods

vars = {}  # persistent variables containing the result after execution and pass between modules
settings = {}  # user-defined, module settings

"""
vars = {
    'module_1': 'return_data_1
    'mod_2': 'return_data_2
}

settings = {
    # imported from the config file
    'module_1': {
        'setting_1': 'value',
        'setting_2': 'value',
    },
    'module_2': {
            'setting_1': 'value',
            'setting_2': 'value',
        }
}
"""

manager = PluginManager(directories_list=["../modules"])
manager.setCategoriesFilter({
    "Modules": mods.CSModule
})
manager.setPluginInfoExtension('plugin')

manager.collectPlugins()

for plugin in manager.getPluginsOfCategory("Modules"):

    name = plugin.name
    kwargs = {**settings, **vars}  # overwrites settings
    vars[name] = plugin.plugin_object.main(kwargs=kwargs)