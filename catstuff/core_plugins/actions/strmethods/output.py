from catstuff.tools.vars import VarPool
import inspect, collections
# from shutil import get_terminal_size

__version__ = '1.0'


def print_info(show_replaced=False, show_builtins=False, sort_by='method', sort_order='ascending'):
    tab_width = 4
    attrs = ['method', 'plugin']

    def get_plugin_method_attr(plugin, method, attr: str):
        try:
            def case_signature():
                sig = inspect.signature(method)
                try:
                    arg1 = list(sig.parameters.items())[0]
                except IndexError:
                    sig_without_self = sig
                else:  # arg1 exists
                    if 'self' in arg1:
                        params = sig.parameters.copy()
                        del params['self']
                        sig_without_self = sig.replace(parameters=params)
                    else:
                        sig_without_self = sig
                return method.__name__ + str(sig_without_self)
            return {
                'method': lambda : method.__name__,
                'plugin': lambda : plugin.name,
                'doc': lambda : method.__doc__,
                'signature': case_signature
            }[attr]()
        except KeyError:
            raise NotImplementedError('Unknown attr {}. You made a type'.format(attr))


    def get_plugin_methods(plugin) -> list:
        """ Returns a list of subclass methods of a StrMethod plugin"""

        # Use of the predicate inspect.ismethod will not work since it requires an instance, not a class object. This
        # may cause problems while checking parent classes that require arguments during init

        # methods = {<function of method>, ...}
        methods = {member[1] for member in inspect.getmembers(plugin.plugin_object.__class__,
                                                              predicate=inspect.isfunction)}
        parents = inspect.getmro(plugin.plugin_object.__class__)[1:]
        parent_methods = set()
        for parent in parents:
            # the routine predicate also handles the python builtin types
            parent_methods.update({member[1] for member in inspect.getmembers(parent, predicate=inspect.isroutine)})

        subclass_methods = methods - parent_methods  # return only the methods defined in the class
        return list(subclass_methods)

    def max_str_len(name: str, values: list):
        """ Returns the max string length for parameter name versus a list of values """

        max_len = len(name)
        for value in values:
            max_len = max(max_len, len(str(value)))
        return max_len

    vars_ = VarPool()
    manager = vars_.get('manager', app='catstuff')
    plugins = manager.getPluginsOfCategory('StrMethod')

    method_attrs = {}
    # method_attrs = {
    #     method: {
    #         attr: value
    #     }
    # }
    for plugin in plugins:
        methods = get_plugin_methods(plugin)
        for method in methods:
            method_attrs.update({method: {attr: get_plugin_method_attr(plugin, method, attr) for attr in attrs}})

    attr_lens = {attr: max_str_len(attr, [method[attr] for method in method_attrs.values()]) for attr in attrs}

    # TODO: Handle long format strings (text wrapping)

    header = "\t".join(["{attr:{str_len}}".format(attr=attr.capitalize(), str_len=attr_lens[attr])
                     for attr in attrs]).replace("\t", " "*tab_width)  # expandtabs not formatting correctly...
    border = "\t".join(["{attr:{str_len}}".format(attr='-'*attr_lens[attr], str_len=attr_lens[attr])
                     for attr in attrs]).replace("\t", " "*tab_width)

    print(header)
    print(border)

    sort_rev = {'ascending' : False, 'asc': False,
                'descending': True, 'des': True}[sort_order.lower()]
    try:
        method_attrs = collections.OrderedDict(
            sorted(method_attrs.items(),
                   key=lambda method: (
                       str(method[1][sort_by]).lower(),
                       method[0].__name__.lower()),
                   reverse=sort_rev))
    except KeyError:  # sort by name, case-insensitive
        method_attrs = collections.OrderedDict(sorted(method_attrs.keys(),
                                                      key=lambda method: method.__name__.lower(), reverse=sort_rev))

    for method_attr in method_attrs.values():  # print values
        line = "\t".join(["{attr:{str_len}}".format(attr=method_attr[attr], str_len=attr_lens[attr])
                         for attr in attrs]).replace("\t", " "*tab_width)
        print(line)


def print_wrapper(args):
    if args.all:
        args.replaced = True
        args.builtins = True
    print_info(show_replaced=args.replaced, show_builtins=args.builtins,
               sort_by=args.sort_by, sort_order=args.sort_order)
