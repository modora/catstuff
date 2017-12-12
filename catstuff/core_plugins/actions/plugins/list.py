from catstuff.tools.config import PluginConfig
from catstuff.tools.vars import VarPool
# from shutil import get_terminal_size

__version__ = '1.2.1'


def print_info(attrs: list, tab_width=4, sort_by='name', sort_order='ascending'):
    def get_plugin_attr(plugin, attr):
        """ Returns the attribute of a plugin"""
        special_attrs = {
            'category'  : plugin.category,
            'categories': str(plugin.categories),
            'path'      : plugin.path + '.py',
        }

        try:
            return special_attrs[attr]
        except KeyError:
            return PluginConfig.from_yapsy(plugin).get(attr, default='')

    def max_str_len(attr, plugin_attrs):
        """ Returns the max string length for some attribute"""

        max_len = len(attr)
        for plugin_attr in plugin_attrs.values():
            max_len = max(max_len, len(plugin_attr[attr]))
        return max_len

    vars_ = VarPool()
    manager = vars_.get('manager', app='catstuff')
    plugins = manager.getAllPlugins()


    # {plugin_name: {attr: value, ...}, ...}
    plugin_attrs = {plugin.name: {attr: get_plugin_attr(plugin, attr) for attr in attrs} for plugin in plugins}

    attr_lens = {attr: max_str_len(attr, plugin_attrs) for attr in attrs}

    # TODO: Handle long format strings (text wrapping)

    header = "\t".join(["{attr:{str_len}}".format(attr=attr.capitalize(), str_len=attr_lens[attr])
                     for attr in attrs]).replace("\t", " "*tab_width)  # expandtabs not formatting correctly...
    border = "\t".join(["{attr:{str_len}}".format(attr='-'*attr_lens[attr], str_len=attr_lens[attr])
                     for attr in attrs]).replace("\t", " "*tab_width)

    print(header)
    print(border)

    sort_rev = {'ascending': False, 'asc': False,
                'descending': True, 'des': True}[sort_order.lower()]
    try:
        plugins = sorted(plugins,
                         key=lambda plugin: (
                             str(plugin_attrs[plugin][sort_by]).lower(),
                             plugin.name.lower()),
                         reverse=sort_rev)
    except KeyError:  # sort by name, case-insensitive
        plugins = sorted(plugins, key=lambda plugin: plugin.name.lower(), reverse=sort_rev)

    for plugin in plugins:  # print values
        line = "\t".join(["{attr:{str_len}}".format(attr=plugin_attrs[plugin.name][attr], str_len=attr_lens[attr])
                         for attr in attrs]).replace("\t", " "*tab_width)
        print(line)


def print_wrapper(args):
    print_info(args.args, tab_width=args.t, sort_by=args.sort_by, sort_order=args.sort_order)