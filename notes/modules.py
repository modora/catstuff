from yapsy.PluginManager import PluginManager
import os
import traceback, logging
import catstuff.tools.plugins
import catstuff.core.plugins
import catstuff.tools.db
import catstuff.tools.common
import catstuff
import yaml

logging.basicConfig()
_base = os.path.dirname(os.path.realpath(catstuff.__file__))

## Settings
global_settings = {
    'path': r'C:\Users\S\PycharmProjects\catstuff\LICENSE',
}
settings = {
    'filelist': {
        'path': r'C:\Users\S\PycharmProjects\catstuff\tests',
        'max_depth': -1,
        'exclude': ['*.py'],
        'include': ['*.yml'],
        'mode': 'blacklist'
    },
    'checksum': {
        'methods': ['crc32', 'md5']
    }
}  # user-defined, module settings

tasks = [
    'Success', 'Success', 'Fail', 'Success', 'Nonexistent plugin', 'filelist', 'checksum'
]


manager = PluginManager(plugin_info_ext='plugin')
manager.setCategoriesFilter({
    'Modules': catstuff.tools.plugins.CSModule,
    'Collections': catstuff.tools.plugins.CSCollection,
})
manager.setPluginPlaces([os.path.join(_base, 'modules')])

manager.collectPlugins()  # Import and categorize plugins

catstuff.tools.common.title('Manager Properties')
print('Categories:', manager.getCategories())
for category in manager.getCategories():
    print('\t', category, ":",
          [plugin.name for plugin in manager.getPluginsOfCategory(category)])

catstuff.tools.common.title('Plugin Properties')
for plugin in manager.getPluginsOfCategory('Modules'):
    catstuff.tools.common.print_attr(plugin)
    catstuff.tools.common.border(symbol='*', border_length=50)

catstuff.tools.common.title('Main')
catstuff.core.plugins.main(global_settings=global_settings,
                           settings=settings,
                           tasks=tasks)

catstuff.tools.common.title('Master')
master = catstuff.tools.db.Master(path=global_settings['path'])
catstuff.tools.common.title('raw', border_length=50, symbol='*')
print(yaml.dump(master.get_raw()))
catstuff.tools.common.title('linked', border_length=50, symbol='*')
print(yaml.dump(master.get()))