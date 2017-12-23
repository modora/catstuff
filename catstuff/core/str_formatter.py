from .vars import CSVarPool
import pyparsing as pp
from collections import namedtuple

_Expression = namedtuple('Expression', 'name args kwargs')
_TemplateVar = namedtuple('TemplateVar', 'var funcs')
_PoolVar = namedtuple('PoolVar', 'var')


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
    manager = CSVarPool.get('manager', app='catstuff')
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
        Added bool_literal, NoneType, set, and string as types
        More robust forms of builtins

    Copyright, 2006, by Paul McGuire
    '''

    '''
    Real cases:
    Case 1: optional_sign + int + dot + optionals (1.0, 1., 1.e3, +1.0)
    Case 2: optionals + dot + int + optionals (.101, -.1e-2)
    Case 3: int + e + int (1e3)
    '''
    real_literal = (
        pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums) + "." +
                   pp.Optional(pp.Word(pp.nums)) +
                   pp.Optional(pp.oneOf("e E") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums))) |
        pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Optional(pp.Word(pp.nums)) + "." +
                   pp.Word(pp.nums) +
                   pp.Optional(pp.oneOf("e E") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums))) |
        pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums) +
                   pp.oneOf("e E") + pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums))
    )
    real_literal.setName("real").setParseAction(lambda toks: float(toks[0]))

    int_literal = pp.Combine(pp.Optional(pp.oneOf("+ -")) + pp.Word(pp.nums))
    int_literal.setName("int_literal").setParseAction(lambda toks: int(toks[0]))

    bool_literal = pp.Keyword('True').setParseAction(pp.replaceWith(True)) | \
                   pp.Keyword('False').setParseAction(pp.replaceWith(False))

    None_literal = pp.Keyword('None').setParseAction(pp.replaceWith(None))

    string_literal = (pp.QuotedString("'", escChar='\\') | pp.QuotedString('"', escChar='\\'))
    list_literal = pp.Forward()
    tuple_literal = pp.Forward()
    dict_literal = pp.Forward()
    set_literal = pp.Forward()

    builtins = real_literal | int_literal | bool_literal | None_literal | string_literal | \
               list_literal | tuple_literal | dict_literal | set_literal

    # Using pp.Group is necessary to handle nested lists
    list_literal << pp.Group(pp.Suppress('[') + (
        pp.delimitedList(builtins) + pp.Optional(pp.Suppress(",")) |
        pp.Empty()
    ) + pp.Suppress(']'))
    list_literal.setParseAction(lambda toks: list(toks.asList()))

    tuple_literal << (pp.Suppress("(") + (
        pp.delimitedList(builtins) + pp.Optional(pp.Suppress(",")) |
        pp.Empty()
    ) + pp.Suppress(")"))
    tuple_literal.setParseAction(lambda toks: tuple(toks.asList()))

    dictEntry = pp.Group(builtins + pp.Suppress(':') + builtins)
    dict_literal << (pp.Suppress('{') + (
        pp.delimitedList(dictEntry) + pp.Optional(pp.Suppress(",")) |
        pp.Empty()
    ) + pp.Suppress('}'))
    dict_literal.setParseAction(lambda toks: dict(toks.asList()))

    set_literal << (
        (pp.Suppress("{") + (
            pp.delimitedList(builtins) + pp.Optional(pp.Suppress(","))
        ) + pp.Suppress("}")).setParseAction(lambda toks: set(toks.asList())) |
        pp.Keyword('set()').setParseAction(pp.replaceWith(set()))
    )

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

        func_name = identifier.copy()
        keyword = identifier.copy()
        pool_var = identifier.copy().setParseAction(lambda toks: _PoolVar(var=toks[0]))
        # example: In 'func(a,b)', arg is a single argument: 'a' or 'b'

        '''
        The named argument wraps the output in a dict
        The parsed output of arg is wrapped in a tuple so the filter won't mistake an dict type arg
        '''
        arg = (expression | pool_var | _Parsers.builtins).setParseAction(lambda toks: (toks[0],))
        named_arg = (keyword + pp.Suppress('=') + arg).setParseAction(lambda toks: {toks[0]: toks[1][0]})

        expression << (func_name + pp.Suppress('(') +
                       pp.Optional(pp.delimitedList(named_arg | arg)).setParseAction(filter_args) +
                       pp.Suppress(')'))

        # TODO: We can do a messy implementation of the expression parser
        # Assume parens are suppressed in the example implementations below
        # The parse action will occur at the delim list
        # Case 1: All args (func_name + '(' + delimitedList(arg) + ')')
        # Case 2: All kwargs (func_name + '(' + delimitedList(named_arg) + ')')
        # Case 3: No args/kwargs -- technically a subset of case 1
        # Case 4: Mixed (to be tested -- func_name + '(' + delimitedList(arg) + ',' + delimitedList(named_arg) + ')' )

        def expression_parseaction(toks):
            name = toks[0]
            try:
                args = toks[1][0]
                kwargs = toks[1][1]
            except IndexError:
                args = []
                kwargs = {}
            return _Expression(name=name, args=args, kwargs=kwargs)

        expression.setParseAction(expression_parseaction)

        return expression

    @staticmethod
    def string(allow_private=False):
        if allow_private:  # private functions are restricted!
            identifier = pp.Word(pp.alphas + "_", pp.alphanums + "_")
        else:
            identifier = pp.Word(pp.alphas, pp.alphanums + "_")

        template = pp.Forward()

        pool_var = identifier.copy()
        var = _Parsers.builtins | pool_var.setParseAction(lambda name: _PoolVar(name)) | template
        special_chars = pp.Keyword('$$').setParseAction(pp.replaceWith('$'))
        template << (pp.Suppress('$') + pp.Suppress('{') +
                    var +
                    pp.ZeroOrMore(pp.Suppress('.') + _Parsers.expression(allow_private=allow_private)) +
                    pp.Suppress('}'))

        def template_parse_action(toks):
            name = toks[0]
            try:
                funcs = toks[1:]
            except IndexError:
                funcs = []
            return _TemplateVar(name, funcs)

        template.setParseAction(template_parse_action)

        restricted_chars = '$'
        printables = ''.join(c for c in (set(pp.printables) - set(restricted_chars)))
        string = pp.ZeroOrMore(special_chars | template |
                               pp.Combine(pp.Word(printables + ' ')).leaveWhitespace())

        return string


class StringParser:
    def __init__(self, allow_private=False):
        # TODO: add VarPool list as arg
        self.allow_private = allow_private
        self._parsers = _Parsers(allow_private=allow_private)

    def parse(self, instring: str):
        return self._parsers.string.parseString(instring)

    def get_var(self, var, *, app_list, pool=None, default=...):
        pool = CSVarPool if pool is None else pool
        return pool.get_var_priority(var, app_list=app_list, default=default)

    def eval_var(self, var, funcs=(), CSStr=None, **kwargs):
        if CSStr is None:
            CSStr = CSStrConstructor()

        if isinstance(var, _PoolVar):
            var = self.get_var(var[0], **kwargs)
            # TODO: TO BE IMPLEMENTED
        elif isinstance(var, _TemplateVar):
            v, funcs = var
            var = self.eval_var(v, funcs, **kwargs)

        obj = var
        for func in funcs:
            func_name, args, kws = func
            args = [self.eval_var(arg) if isinstance(arg, _TemplateVar) else arg for arg in args]
            kws = {key: (self.eval_var(value) if isinstance(value, _TemplateVar) else value) for key, value in
                   kws.items()}

            obj = getattr(CSStr(obj), func_name)(*args, **kws)  # Evaluate the object

        return obj

    def eval_string(self, instring, **kwargs):
        strings = self.parse(instring).asList()
        for i, string in enumerate(strings):
            if isinstance(string, _TemplateVar):
                var, funcs = string
                strings[i] = self.eval_var(var, funcs, **kwargs)
        return ''.join(strings)

# TODO: allow python formatter to be used on templates