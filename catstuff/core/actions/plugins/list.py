from catstuff.core.manager import manager
from catstuff.tools.config import PluginConfig
# from shutil import get_terminal_size

__version__ = '1.0'


def print_info(attrs: list, tab_width=4):
    plugins = manager.getAllPlugins()
    format_list = []  # list of tuples in the form (attr_name, str_length)
    for attr in attrs:
        max_len = len(attr)

        for plugin in plugins:
            config = PluginConfig.from_yapsy(plugin)
            value = config.get(attr.lower(), default='')  # ini options imported as lower

            max_len = max(max_len, len(value))
        format_list.append((attr, max_len))

    # TODO: Handle long format strings (text wrapping)

    print("\t".join(["{attr:{str_len}}".format(attr=format[0], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # expandtabs not formatting correctly...
    print("\t".join(["{attr:{str_len}}".format(attr='-'*format[1], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # border
    for plugin in plugins:
        config = PluginConfig.from_yapsy(plugin)
        print("\t".join(["{attr:{str_len}}".format(attr=config.get(format[0].lower(), default=''), str_len=format[1])
                         for format in format_list]).replace("\t", " "*tab_width))

def print_wrapper(args):
    print_info(args.args, tab_width=args.t)


if __name__ == '__main__':
    print_wrapper()