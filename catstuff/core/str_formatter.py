from .manager import CSPluginManager
from .vars import VarPool


def CSStrConstructor(remap=None):
    """
    Constructs the CSStr object for string formatting
    :param remap: if multiple classes contain the same attribute, use this to specify which class to inherit from
    {'attr': 'plugin_name'}
    :type dict
    :return:
    :rtype: CSStr
    """
    remap = remap or {}
    assert isinstance(remap, dict)
    manager = VarPool().get('manager', app='catstuff', default=CSPluginManager())
    bases = set()
    dict_ = {}

    # Construct the base settings
    for plugin in manager.getPluginsOfCategory('StrMethod'):
        bases.add(plugin.plugin_object.__class__)
        dict_.update(plugin.plugin_object.__class__.__dict__)
    # Manual attribute inheritance specification
    for attr, plugin_name in remap.items():
        plugin = manager.getPluginByName(plugin_name, 'StrMethod')
        try:
            value = plugin.plugin_object.__class__.__dict__[attr]
            dict_.update({attr: value})
        except AttributeError:
            # TODO: raise "plugin does not exist"
            raise
        except KeyError:
            print("{plugin} does not have {attr} attribute".format(plugin=plugin_name, attr=attr))

    return type('CSStr', tuple(bases), dict_)

# TODO: allow functions to operate on literal strings
# TODO: allow python formatter to be used on templates