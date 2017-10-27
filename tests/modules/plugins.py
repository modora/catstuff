from yapsy.PluginManager import PluginManager
import os
import traceback, logging
import catstuff.tools.modules as mods

from catstuff import __file__ as __base__
__base__ = os.path.dirname(__base__)

manager = PluginManager(plugin_info_ext='plugin')
manager.setCategoriesFilter({
    'Modules': mods.CSCollection,
})
manager.setPluginPlaces([os.path.join(__base__, 'modules')])

manager.collectPlugins()  # Import and categorize plugins

print('------------------------------------------------------------------------------------------')
print('Manager Properties')
print('------------------------------------------------------------------------------------------')
print('Categories:', manager.getCategories())

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
args = {}
kwargs = {}

for plugin in manager.getAllPlugins():
    print("Name:", plugin.name)
    a = args.get(plugin.name, [])
    kw = kwargs.get(plugin.name, {})
    try:
        print("Output:", plugin.plugin_object.main(a, kw))
    except Exception as e:
        print("FAILED TO EXECUTE '{name}': {error}".format(name=plugin.name, error=e))
    print('---------------------------------------------')