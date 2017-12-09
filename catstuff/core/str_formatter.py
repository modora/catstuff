from .manager import CSPluginManager
from .vars import VarPool
import pyparsing as pp
from collections import namedtuple

class _Globals:
    Func = namedtuple('Func', 'name args kwargs')
    CSVar = namedtuple('CSVar', 'name funcs')
    PoolVar = namedtuple('PoolVar', 'name')
    CSStr = CSStrConstructor()


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

class _Parsers:
    """ Container for numerous pyparsing parsers"""
    '''
    Modified version parsePythonValue.py

    Changes:
        Renamed some of the variables
        Added boolean, None, set, and string as types

    Copyright, 2006, by Paul McGuire
    '''
    integer = pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums)) \
        .setName("integer").setParseAction(lambda toks: int(toks[0]))
    real = pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums) + "." +
                      pp.Optional(pp.Word(pp.nums)) +
                      pp.Optional(pp.oneOf("e E") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums))) \
        .setName("real").setParseAction(lambda toks: float(toks[0]))
    boolean = pp.Literal('True').setParseAction(lambda x: True) | pp.Literal('False').setParseAction(
        lambda x: False)

    # TODO: NoneStr doesn't work
    # pyparsing seems to have an internal method that checks if it's returning None and replaces it with the string
    # literal
    NoneStr = pp.Literal('None').setParseAction(lambda x: None)

    string = pp.quotedString.setParseAction(pp.removeQuotes)
    tupleStr = pp.Forward()
    listStr = pp.Forward()
    dictStr = pp.Forward()
    setStr = pp.Forward()

    builtins = real | integer | boolean | NoneStr | string | \
               pp.Group(listStr) | tupleStr | dictStr | setStr

    tupleStr << (pp.Suppress("(") + pp.Optional(pp.delimitedList(builtins)) +
                 pp.Optional(pp.Suppress(",")) + pp.Suppress(")"))
    tupleStr.setParseAction(lambda toks: tuple(toks.asList()))

    listStr << (pp.Suppress('[') + pp.Optional(pp.delimitedList(builtins) +
                                               pp.Optional(pp.Suppress(","))) + pp.Suppress(']'))

    dictEntry = pp.Group(builtins + pp.Suppress(':') + builtins)
    dictStr << (pp.Suppress('{') + pp.Optional(pp.delimitedList(dictEntry) +
                                               pp.Optional(pp.Suppress(","))) + pp.Suppress('}'))
    dictStr.setParseAction(lambda toks: dict(toks.asList()))

    setStr << (pp.Suppress("{") + pp.Optional(pp.delimitedList(builtins)) +
               pp.Optional(pp.Suppress(",")) + pp.Suppress("}"))
    setStr.setParseAction(lambda toks: set(toks.asList()))

    def __init__(self, allow_private=False):
        self._allow_private = allow_private
        self.expression = self.expression(allow_private=self.allow_private)
        self.string = self.string(allow_private=self.allow_private)

    @property
    def allow_private(self):
        return self._allow_private

    @staticmethod
    def expression(allow_private=False):
        def filter_args(delim_list: list):
            """ Filters the results from a delimited list to return a list of args and kwargs"""
            # TODO: This implementation has the issue that args and kwargs can be entered in any order and kwargs can be repeated
            #   ie func(kw1=1, 2) and func(kw1=1, kw1=2) would be a valid
            args = []
            kwargs = {}
            for arg in delim_list:
                if isinstance(arg, dict):
                    kwargs.update(arg)
                else:
                    args.append(arg[0])  # arguments are wrapped in a single element tuple
            return args, kwargs

        # example: 'func(a,b)' is an expression with 'func' as func_name and [a,b] as arguments
        expression = pp.Forward()

        if allow_private:  # private functions are restricted!
            identifier = pp.Word(pp.alphas + "_", pp.alphanums + "_")
        else:
            identifier = pp.Word(pp.alphas, pp.alphanums + "_")

        func_name = identifier
        keyword = identifier
        # example: In 'func(a,b)', arg is a single argument: 'a' or 'b'

        '''
        The named argument wraps the output in a dict
        The parsed output of arg is wrapped in a tuple so the filter won't mistake an dict type arg
        '''
        arg = (pp.Group(expression) | identifier | _Parsers.builtins).setParseAction(lambda toks: (toks[0],))
        named_arg = (keyword + pp.Suppress('=') + arg).setParseAction(lambda toks: {toks[0]: toks[1][0]})

        expression << (func_name + pp.Suppress('(') +
                       pp.Optional(pp.delimitedList(named_arg | arg)).setParseAction(filter_args) +
                       pp.Suppress(')'))

        def expression_parseaction(toks):
            name = toks[0]
            try:
                args = toks[1][0]
                kwargs = toks[1][1]
            except IndexError:
                args = []
                kwargs = {}
            return _Globals.Func(name=name, args=args, kwargs=kwargs)

        expression.setParseAction(expression_parseaction)

        return expression

    @staticmethod
    def string(allow_private=False):
        if allow_private:  # private functions are restricted!
            identifier = pp.Word(pp.alphas + "_", pp.alphanums + "_")
        else:
            identifier = pp.Word(pp.alphas, pp.alphanums + "_")
        var = _Parsers.builtins | identifier.setParseAction(lambda name: _Globals.PoolVar(name))
        special_chars = pp.Literal('$$').setParseAction(lambda x: '$')
        template = pp.Suppress('$') + pp.Suppress('{') + \
                   var + \
                   pp.ZeroOrMore(pp.Suppress('.') + _Parsers.expression(allow_private=allow_private)) + \
                   pp.Suppress('}')

        def template_parse_action(toks):
            name = toks[0]
            try:
                funcs = toks[1:]
            except IndexError:
                funcs = []
            return _Globals.CSVar(name, funcs)

        template.setParseAction(template_parse_action)

        restricted_chars = '$'
        printables = ''.join(c for c in (set(pp.printables) - set(restricted_chars)))
        string = pp.ZeroOrMore(special_chars | pp.Group(template) |
                               pp.Combine(pp.Word(printables + ' ')).leaveWhitespace())

        return string

class StringParser:
    def __init__(self, allow_private=False):
        # TODO: add VarPool list as arg
        self.allow_private = allow_private
        self._parsers = _Parsers(allow_private=allow_private)

    def parse(self, instring: str) -> list:
        return self._parsers.string.parseString(instring)

    def eval_var(self, var: _Globals.CSVar, pool=None):
        name, funcs = var
        if isinstance(name, _Globals.PoolVar):
            # TODO: TO BE IMPLEMENTED

        obj = _Globals.CSStr(name)
        for func in funcs:
            func_name, args, kwargs = func
            args = [self.eval_var(arg) if isinstance(arg, _Globals.CSVar) else arg for arg in args]
            kwargs = {key: (self.eval_var(value) if isinstance(value, _Globals.CSVar) else value) for key, value in
                      kwargs.items()}

            obj = getattr(obj, func_name)(*args, **kwargs)  # Evaluate the object

        return obj

# TODO: allow python formatter to be used on templates