from yapsy.PluginManager import PluginManager
import os
import traceback, logging
import catstuff.tools.modules
import catstuff.core.modules

from catstuff import __file__ as __base__
__base__ = os.path.dirname(os.path.realpath(__base__))

## Settings
global_settings = {
    'path': r'C:\Users\S\PycharmProjects\catstuff\LICENSE',
}
settings = {
    'filelist': {
        'path': r'C:\Users\S\PycharmProjects\catstuff\tests',
        'max_depth': -1,
        'exclude': ['*.py']
    },
    'checksum': {
        'methods': 'crc32'
    }
}  # user-defined, module settings

tasks = [
    'Success', 'Success', 'Fail', 'Success', 'Nonexistent plugin', 'filelist'
]


manager = PluginManager(plugin_info_ext='plugin')
manager.setCategoriesFilter({
    'Modules': catstuff.tools.modules.CSCollection,
})
manager.setPluginPlaces([os.path.join(__base__, 'modules')])

manager.collectPlugins()  # Import and categorize plugins

print('------------------------------------------------------------------------------------------')
print('Manager Properties')
print('------------------------------------------------------------------------------------------')
print('Categories:', manager.getCategories())
for category in manager.getCategories():
    print('\t', category, ":",
          [plugin.name for plugin in manager.getPluginsOfCategory(category)])

print('------------------------------------------------------------------------------------------')
print('Plugin Properties')
print('------------------------------------------------------------------------------------------')
for plugin in manager.getPluginsOfCategory('Modules'):
    for attr in dir(plugin):
        if attr[0] == "_":
            continue
        print(attr, ":", getattr(plugin, attr))
    print('---------------------------------------------')
print('------------------------------------------------------------------------------------------')
print("Main")
print('------------------------------------------------------------------------------------------')
catstuff.core.modules.main(global_settings=global_settings,
                           settings=settings,
                           tasks=tasks)