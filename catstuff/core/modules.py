from yapsy.PluginManager import PluginManager
import catstuff.tools.modules
import logging
import os

__dir__ = os.path.dirname(os.path.realpath(__file__))

"""
global_settings = {
    'setting1': value,
    'setting2': value
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

vars = {
    'module_1': 'return_data_1
    'mod_2': 'return_data_2
}

tasks = [
'Mod 1 Name',
'Mod 2 Name',
'Mod 3 Name'
]
"""

_restricted_plugin_names = {'path'}

manager = PluginManager()
manager.setPluginPlaces([
    os.path.join(__dir__, "../modules")
])
manager.setCategoriesFilter({
    "Modules": catstuff.tools.modules.CSModule
})
manager.setPluginInfoExtension('plugin')


def main(global_settings={}, settings={}, tasks=[]):
    vars = {}
    manager.collectPlugins()

    for task in tasks:
        plugin = manager.getPluginByName(task, category="Modules")
        if plugin is None:
            print("No plugin with name {} was found, skipping".format(task))
            continue
        name = plugin.name

        if name in _restricted_plugin_names:
            raise NameError("The name {} is a forbidden plugin name, rename it!!".format(name))

        try:
            import yaml
            from catstuff.tools.common import ExplicitDumper
            print("Executing '{name}' with arguments:".format(name=name))
            print("\t" + yaml.dump({
                **global_settings,
                **settings.get(name, {}),
                **vars,
            }, Dumper=ExplicitDumper, default_flow_style=False, indent=2).replace("\n", "\n\t"))

            vars[name] = plugin.plugin_object.main(**{
                **global_settings,
                **settings.get(name, {}),
                **vars,
            })
        except Exception as e:
            print("Failed to execute {} module:".format(name), e)
            pass

