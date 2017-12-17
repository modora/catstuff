import inspect, collections, re
from catstuff import core
# from shutil import get_terminal_size

__version__ = '1.1.3'


def print_info(attrs: list, show_replaced=False, show_builtins=False,
               sort_by=None, sort_order='ascending',
               tab_width=4):
    if sort_by is None:
        sort_by = attrs[0]

    def get_method_attr(method, attr: str, plugin=None):
        if plugin is not str:
            if attr == 'method':
                return method.__name__
            elif attr == 'plugin':
                return plugin.name
            elif attr == 'doc':
                return (method.__doc__ or '').strip()
            elif attr == 'signature':
                sig = inspect.signature(method)

                # remove the leading self/cls argument
                if list(sig.parameters.keys())[0] in {'self', 'cls'}:
                    params = list(sig.parameters.copy().values())
                    del params[0]
                    sig = sig.replace(parameters=params)

                return method.__name__ + str(sig)
        else:
            if attr == 'method':
                return method.__name__
            elif attr == 'plugin':
                return '-'
            elif attr == 'doc':

                regex = re.compile('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
                if method.__name__ == 'maketrans':
                    return re.split(regex, method.__doc__.replace('\n', " "))[0].replace('S', 'str')
                # Too lazy to copy, paste. Just return the first sentence of the paragraph
                S_char = re.compile(r'\b[S]\b')  # replace S with str
                doc = re.split(regex, method.__doc__.split('\n', 2)[2].replace('\n', " "))[0]
                return re.sub(S_char, 'str', doc)
            elif attr == 'signature':
                if method.__name__ == 'maketrans':
                    return 'maketrans(x[, y[, z]])'
                return method.__doc__.split('\n', 1)[0][2:]  # i was too lazy to write them out myself



    def get_plugin_methods(plugin) -> list:
        """ Returns a list of subclass methods of a StrMethod plugin"""
        return get_subclass_methods(plugin.plugin_object.__class__)


    def get_subclass_methods(obj) -> list:
        """ Returns all methods defined in some subclass"""
        # Use of the predicate inspect.ismethod will not work since it requires an instance, not a class object. This
        # may cause problems while checking parent classes that require arguments during init

        # methods = {<function of method>, ...}
        # do not show private methods
        methods = {member[1] for member in inspect.getmembers(obj, predicate=inspect.isroutine) if member[0][0] != '_'}
        parents = inspect.getmro(obj)[1:]
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

    manager = core.vars.CSVarPool.get('manager', app='catstuff')
    plugins = manager.getPluginsOfCategory('StrMethod')

    CSStr = core.str_formatter.CSStrConstructor()

    method_attrs = {}  # a dict containing details of all of the methods found in some StrMethod plugin class
    # method_attrs = {
    #     method: {
    #         attr: value
    #     }
    # }

    for plugin in plugins:
        plugin_methods = get_plugin_methods(plugin)
        for method in plugin_methods:
            method_attrs.update({method: {attr: get_method_attr(method, attr, plugin=plugin) for attr in attrs}})

    methods = set()
    methods.update(method_attrs.keys()) if show_replaced else methods.update(get_subclass_methods(CSStr))
    if show_builtins:
        str_methods = get_subclass_methods(str)
        methods.update(str_methods)
        for method in str_methods:
            method_attrs.update({method: {attr: get_method_attr(method, attr, plugin=str) for attr in attrs}})

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
    print_info(args.attrs,
               show_replaced=args.replaced, show_builtins=args.builtins,
               sort_by=args.sort_by, sort_order=args.sort_order,
               tab_width=args.t)
