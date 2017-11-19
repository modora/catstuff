from catstuff.core.manager import manager
from catstuff.tools.config import PluginConfig
# from shutil import get_terminal_size

def print_info(attrs: list, tab_width=4):
    actions = manager.getPluginsOfCategory('Actions')
    format_list = []  # list of tuples in the form (attr_name, str_length)
    for attr in attrs:
        max_len = len(attr)

        for action in actions:
            config = PluginConfig.from_yapsy(action)
            value = config.get(attr.lower(), default='')  # ini options imported as lower

            max_len = max(max_len, len(value))
        format_list.append((attr, max_len))

    # TODO: Handle long format strings (text wrapping)

    print("\t".join(["{attr:{str_len}}".format(attr=format[0], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # expandtabs not formatting correctly...
    print("\t".join(["{attr:{str_len}}".format(attr='-'*format[1], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # border
    for action in actions:
        config = PluginConfig.from_yapsy(action)
        print("\t".join(["{attr:{str_len}}".format(attr=config.get(format[0].lower(), default=''), str_len=format[1])
                         for format in format_list]).replace("\t", " "*tab_width))
