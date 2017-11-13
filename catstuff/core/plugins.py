from yapsy.PluginManager import PluginManager
import catstuff.tools.plugins
import catstuff.tools.common
import logging, logging.handlers, datetime
import os
import json


_dir = os.path.dirname(os.path.realpath(__file__))

log_file = os.path.join(_dir, '../logs/core/plugins.log')
catstuff.tools.common.touch(log_file)
# logging.basicConfig(filename=log_file, level=logging.DEBUG)

log_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024,
                                                   backupCount=2, encoding=None, delay=0)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s - %(names)s - %(funcName)s(%(lineno)d): %(message)s'
))
log_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('modules')
logger.setLevel(logging.DEBUG)
# logger.addHandler(log_handler)  # fix this

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
    os.path.join(_dir, "../modules")
])
manager.setCategoriesFilter({
    "Modules": catstuff.tools.plugins.CSModule
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
            plugin_settings = settings.get(name, {})

            args = {
                **global_settings,
                **plugin_settings,
                'vars': {**vars},
            }

            print("Executing '{name}' with arguments:".format(name=name))
            print(json.dumps(args))

            vars[name] = plugin.plugin_object.main(**args)
        except Exception as e:
            print("Failed to execute {} module:".format(name), e)
            logger.error("Failed to execute {} module:".format(name), exc_info=True)


if __name__ == '__main__':
    main()