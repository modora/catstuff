from catstuff.core.manager import CSPluginManager
from catstuff.tools.config import PluginConfig
from catstuff.tools.vars import VarPool
# from shutil import get_terminal_size

__version__ = '1.1'


def print_info(attrs: list, tab_width=4, sort_attr='name', sort_order='ascending'):
    def get_info(attr: str, plugin):
        attr = attr.lower()

        if attr in {'category', 'categories', 'path'}:
            value = {
                'category': plugin.category,
                'categories': str(plugin.categories),
                'path': plugin.path + '.py'
            }[attr]
        else:  # by default, get attr from config
            config = PluginConfig.from_yapsy(plugin)
            value = config.get(attr, default='')  # ini options imported as lower
        return value

    vars_ = VarPool()
    manager = vars_.get('manager', app='catstuff')
    plugins = manager.getAllPlugins()

    sort_rev = {'ascending': False, 'descending': True}.get(sort_order, False)
    try:
        plugins.sort(key=lambda plugin: str(get_info(sort_attr, plugin)).lower(),
                     reverse=sort_rev)
    except AttributeError:  # sort by name, case-insensitive
        plugins.sort(key=lambda plugin: plugin.name.lower(),
                     reverse=sort_rev)

    format_list = []  # list of tuples in the form (attr_name, str_length)
    for attr in attrs:
        max_len = len(attr)

        for plugin in plugins:
            value = get_info(attr, plugin)
            max_len = max(max_len, len(value))
        format_list.append((attr, max_len))

    # TODO: Handle long format strings (text wrapping)

    print("\t".join(["{attr:{str_len}}".format(attr=format[0].capitalize(), str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # expandtabs not formatting correctly...
    print("\t".join(["{attr:{str_len}}".format(attr='-'*format[1], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # border
    for plugin in plugins:  # print values
        print("\t".join(["{attr:{str_len}}".format(attr=get_info(format[0], plugin), str_len=format[1])
                         for format in format_list]).replace("\t", " "*tab_width))


def print_wrapper(args):
    print_info(args.args, tab_width=args.t, sort_attr=args.sort_by, sort_order=args.sort_order)