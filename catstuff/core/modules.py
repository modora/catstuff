from yapsy.PluginManager import PluginManager
import catstuff.tools.modules as mods
import logging

global_settings = {}  # settings used across all modules
settings = {}  # user-defined, module settings
vars = {}  # persistent variables containing the result after execution and pass between modules

tasks = []  # order in which to run plugin tasks

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

manager = PluginManager(directories_list=["../modules"])
manager.setCategoriesFilter({
    "Modules": mods.CSCollection
})
manager.setPluginInfoExtension('plugin')

def main():
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
            vars[name] = plugin.plugin_object.main(**{
                **global_settings,
                **settings.get(name, {}),
                **vars,
            })
        except Exception as e:
            print("Failed to execute {} module:".format(name), e)
            pass


def test():
    manager.collectPlugins()

    for plugin in manager.getPluginsOfCategory("Modules"):

        name = plugin.name
        if name in _restricted_plugin_names:
            raise NameError("The name {} is a forbidden plugin name, rename it!!".format(name))

        try:
            print("Executing {} module".format(name))
            vars[name] = plugin.plugin_object.main(**{
                **global_settings,
                **settings.get(name, {}),
                **vars,
            })
        except Exception as e:
            print("Failed to execute {} module:".format(name), e)
            pass

    import yaml
    print()
    print(yaml.dump(vars))


def test_settings():
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
    vars = {

    }  # persistent variables containing the result after execution and pass between modules

    tasks = [
        'Success', 'Success', 'Fail', 'Success', 'Nonexistent plugin', 'filelist'
    ]

    out = (global_settings, settings, vars, tasks)
    return out


if __name__ == '__main__':
    print('---------------------------------------------------------------------------------------')
    print("Test")
    print('---------------------------------------------------------------------------------------')
    global_settings, settings, vars, tasks = test_settings()
    test()

    print('---------------------------------------------------------------------------------------')
    print("Main")
    print('---------------------------------------------------------------------------------------')
    global_settings, settings, vars, tasks = test_settings()
    main()
    import yaml
    import catstuff.tools.db
    test = catstuff.tools.db.Master()
    uid = test.coll.find_one({}, {"_id": 1})["_id"]
    test.set_uid(uid)

    print()
    print('Vars:')
    print(yaml.dump(vars))
    print()
    print("db")
    print(yaml.dump(test.get()))
