import catstuff.tools as tools
import catstuff.core as core

# from shutil import get_terminal_size)


def print_info(attrs: list, tab_width=4):
    vars_ = core.vars.VarPool()
    manager = vars_.get('manager', 'catstuff')
    actions = manager.getPluginsOfCategory('Action')
    format_list = []  # list of tuples in the form (attr_name, str_length)
    for attr in attrs:
        max_len = len(attr)

        for action in actions:
            config = tools.config.PluginConfig.from_yapsy(action)
            value = config.get(attr.lower(), default='')  # ini options imported as lower

            max_len = max(max_len, len(value))
        format_list.append((attr, max_len))

    # TODO: Handle long format strings (text wrapping)

    print("\t".join(["{attr:{str_len}}".format(attr=format[0], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # expandtabs not formatting correctly...
    print("\t".join(["{attr:{str_len}}".format(attr='-'*format[1], str_len=format[1])
                     for format in format_list]).replace("\t", " "*tab_width))  # border
    for action in actions:
        config = tools.config.PluginConfig.from_yapsy(action)
        print("\t".join(["{attr:{str_len}}".format(attr=config.get(format[0].lower(), default=''), str_len=format[1])
                         for format in format_list]).replace("\t", " "*tab_width))


def print_wrapper(args):
    print_info(args.args, tab_width=args.t)
