from nose.tools import *
from catstuff.core.vars import CSVarPool
from catstuff.core.str_formatter import CSStrConstructor, StringParser
from catstuff.core.str_formatter import _Parsers, _Expression, _TemplateVar, _PoolVar
import pyparsing as pp


class StrFormatter:
    app = 'test'

    def setup(self):
        CSVarPool.setup()
        vars = {
            'foo': 'bar',
            'hello': 'world',
            'one': 1,
            'two': 2,
        }
        CSVarPool.setup(data=vars, app=self.app)  # setup additional vars

    def teardown(self):
        CSVarPool.clear()


class TestCSStr(StrFormatter):
    def setup(self):
        super().setup()
        self.CSStr = CSStrConstructor()

    def test_func(self):
        import inspect
        CSStr = self.CSStr
        ok_(str in inspect.getmro(CSStr), 'str not in CSStr base class')
        ok_(CSStr is not str, 'CSStr and str are the same object')
        ok_(isinstance(CSStr('test str'), str), 'testing with an actual string failed')

    def test_a_function(self):
        """ Requires the 'display' plugin"""
        s = 'literal string'
        s = self.CSStr(s)

        try:
            eq_(s.reverse(), s[::-1])
        except AttributeError:
            ok_(False, 'The reverse() function not found, aborting test -- install the display plugin for it')


class TestParsers:
    class Clipboard:
        expr_reverse = _Expression(name='reverse', args=[], kwargs={})

    from collections import defaultdict
    strings = defaultdict(list)
    invalid_strings = defaultdict(list)
    strings.update({
        'real'      : [
            ('1.0', [1.0]),
            ('1.00001', [1.00001]),
            ('10001.0', [10001.0]),
            ('1.', [1.]),
            ('0.1', [0.1]),
            ('.1', [.1]),
            ('+1.0', [+1.0]),
            ('-1.0', [-1.0]),
            ('-.2', [-.2]),
            ('-1.', [-1.]),
            ('1e3', [1e3]),
            ('1e-3', [1e-3]),
            ('+1.0e2', [+1.0e2]),
            ('-1.0e-2', [-1.0e-2]),
        ],
        'int'       : [
            ('1', [1]),
            ('+1', [1]),
            ('-1', [-1]),
        ],
        'bool'      : [
            ('True', [True]),
            ('False', [False]),
        ],
        'None'      : [
            ('None', [None]),
        ],
        'string'    : [
            ("'hello world'", ['hello world']),
            (r"'hello \' world'", ["hello ' world"]),
            (r"'hello \'foo\' world'", ["hello 'foo' world"]),
        ],
        'list'      : [
            ('[1]', [[1]]),
            ('[True]', [[True]]),
            ('[]', [[]]),
            ('[1, 2]', [[1, 2]]),
            ('[1, True]', [[1, True]]),
            ('[1, ["nested"], 3]', [[1, ['nested'], 3]]),
            ('[1, ["nested", (3,)], 3]', [[1, ['nested', (3,)], 3]]),
        ],
        'tuple'     : [
            ('(1,)', [(1,)]),
            ('(True,)', [(True,)]),
            ('()', [()]),
            ('(1, 2)', [(1, 2)]),
            ('(1, True)', [(1, True)]),
            ('(1, ("nested",), 3)', [(1, ('nested',), 3)]),
            ('(1, ("nested", [3]), 3)', [(1, ('nested', [3]), 3)]),
        ],
        'dict'      : [
            ('{1: 1}', [{1: 1}]),
            ('{}', [{}]),
            ('{"a": "foo"}', [{'a': "foo"}]),
            ('{"1": {}, "2": 2}', [{"1": {}, "2": 2}]),
            ('{"top": {"nested": "dict"}}', [{'top': {'nested': 'dict'}}]),
            ('{"top": {"nested", "set"}}', [{'top': {'nested', 'set'}}]),
        ],
        'set'       : [
            ('{1, 2}', [{1, 2}]),
            ('set()', [set()]),
            ('{1}', [{1}]),
        ],
        'expression': [
            ('func()', [_Expression(name='func', args=[], kwargs={})]),
            ('func(1)', [_Expression(name='func', args=[1], kwargs={})]),
            ('func(1,2)', [_Expression(name='func', args=[1, 2], kwargs={})]),
            ('func(kw=1)', [_Expression(name='func', args=[], kwargs={'kw': 1})]),
            ('func(kw1=1, kw2=2)', [_Expression(name='func', args=[], kwargs={'kw1': 1, 'kw2': 2})]),
            ('func(1,2, kw1=3, kw2=4)', [_Expression(name='func', args=[1, 2], kwargs={'kw1': 3, 'kw2': 4})]),
            ('func(pool_var)', [_Expression(name='func', args=[_PoolVar(var='pool_var')], kwargs={})]),
            ('func(var1, var2)', [_Expression(name='func', args=[_PoolVar('var1'), _PoolVar('var2')], kwargs={})]),
            ('func(kw=var1)', [_Expression(name='func', args=[], kwargs={'kw': _PoolVar('var1')})]),
            ('func(kw1=var1, kw2=var2)', [_Expression(name='func', args=[],
                                                      kwargs={'kw1': _PoolVar('var1'), 'kw2': _PoolVar('var2')})]),
            ('f1(f2())', [_Expression(name='f1', args=[_Expression(name='f2', args=[], kwargs={})],
                                      kwargs={})]),
            ('f1(f2(), f3())', [_Expression(name='f1',
                                            args=[_Expression(name='f2', args=[], kwargs={}),
                                                  _Expression(name='f3', args=[], kwargs={})],
                                            kwargs={})]),
            ('f1(kw1=f2(), kw2=f3())', [_Expression(name='f1',
                                                    args=[],
                                                    kwargs={'kw1': _Expression(name='f2', args=[], kwargs={}),
                                                            'kw2': _Expression(name='f3', args=[], kwargs={})})]),
        ],
        'input': [
            ('literal string', ['literal string']),
            ('string with $$ in it', ['string with ', '$', ' in it']),
            ("string with ${'template'.reverse()} in it",
             ['string with ', _TemplateVar('template', [Clipboard.expr_reverse]), ' in it']),
            ("string with ${${'nested'.reverse()}.reverse()} template",
             ['string with ',
              _TemplateVar(_TemplateVar('nested', [Clipboard.expr_reverse]), [Clipboard.expr_reverse]),
              ' template'])
        ],
    })

    invalid_strings.update({
        'bool': [
            'true',
            'false',
        ],
        'list': [
            '[,]',
        ],
        'tuple': [
            '(,)',
        ],
        'set': [
            '{1, {2}}',
        ],
    })

    @staticmethod
    def parse_string(parser, string, **kwargs):
        obj = _Parsers(**kwargs)
        return getattr(obj, parser).parseString(string)

    @nottest
    def test_template(self, strings: list, parser, **kwargs):
        # strings = [(string, expected), ...]
        for string, expected in strings:
            try:
                result = self.parse_string(parser, string, **kwargs).asList()
            except pp.ParseException as e:
                ok_(False, 'Failed to parse {string}'.format(string=string))
                raise e
            except Exception as e:
                import sys
                raise type(e)(str(e) + ' -- error with parser processing with {}'.format(string)). \
                    with_traceback(sys.exc_info()[2])
            eq_(result, expected, '{string} -> {result!r} != {expected!r}'.format(
                string=string, result=result, expected=expected))

    @nottest
    def test_invalid_template(self, strings: list, parser):
        # strings = [(string, expected), ...]
        @raises(pp.ParseException)
        def parse_invalid_string(parser, string):
            self.parse_string(parser, string)

        for string in strings:
            try:
                parse_invalid_string(parser, string)
            except Exception:
                try:
                    ok_(False, 'Accidentally able to parse {string!r}->{result!r}'.format(
                        string=string, result=self.parse_string(parser, string)))
                except Exception as e:
                    import sys
                    raise type(e)(str(e) + ' -- accidentally able to parse {}'.format(string)).\
                        with_traceback(sys.exc_info()[2])

    def test_real(self):
        strings = self.strings['real']
        self.test_template(strings, 'real_literal')

    def test_int(self):
        strings = self.strings['int']
        self.test_template(strings, 'int_literal')

    def test_bool(self):
        strings = self.strings['bool']
        self.test_template(strings, 'bool_literal')

    def test_None(self):
        strings = self.strings['None']
        self.test_template(strings, 'None_literal')

    def test_string(self):
        strings = self.strings['string']
        self.test_template(strings, 'string_literal')

    def test_list(self):
        strings = self.strings['list']
        self.test_template(strings, 'list_literal')

    def test_tuple(self):
        strings = self.strings['tuple']
        self.test_template(strings, 'tuple_literal')

    def test_dict(self):
        strings = self.strings['dict']
        self.test_template(strings, 'dict_literal')

    def test_set(self):
        strings = self.strings['set']
        self.test_template(strings, 'set_literal')

    def test_builtins(self):
        strings = []
        for type_ in {'real', 'int', 'bool', 'None', 'string', 'list', 'tuple', 'dict', 'set'}:
            strings = strings + self.strings[type_]

        from random import shuffle
        shuffle(strings)

        self.test_template(strings, 'builtins')

    def test_invalid_bool(self):
        strings = self.invalid_strings['bool']
        self.test_invalid_template(strings, 'bool_literal')

    def test_invalid_list(self):
        strings = self.invalid_strings['list']
        self.test_invalid_template(strings, 'list_literal')

    def test_invalid_tuple(self):
        strings = self.invalid_strings['tuple']
        self.test_invalid_template(strings, 'tuple_literal')

    def test_invalid_set(self):
        strings = self.invalid_strings['set']
        self.test_invalid_template(strings, 'set_literal')

    def test_expression(self):
        strings = self.strings['expression']
        self.test_template(strings, 'expression')

    def test_input_string(self):
        # the parser used by the user
        strings = self.strings['input']
        self.test_template(strings, 'string')


class TestStringParser(StrFormatter):
    def setup(self):
        super().setup()
        self.obj = StringParser()

    def test_var_getter(self):
        # Get foo
        foo = self.obj.get_var('foo', pool=CSVarPool, app_list=[self.app])
        eq_(foo, 'bar')

    def test_eval_var(self):
        from collections import namedtuple
        Env = namedtuple('Env', 'var, kwargs, expected')
        env = [
            # (var, **kwargs, expected)
            Env(var='hello',
                kwargs={'funcs': [_Expression(name='reverse', args=[], kwargs={})]},
                expected='olleh'),
            Env(var='hello',
                kwargs={'funcs': [_Expression(name='reverse', args=[], kwargs={}), _Expression(name='reverse', args=[], kwargs={})]},
                expected='hello'),
            Env(var=_PoolVar('foo'),
                kwargs={'funcs': [_Expression(name='reverse', args=[], kwargs={})], 'app_list': [self.app]},
                expected='rab'),
        ]
        for var, kwargs, expected in env:
            try:
                result = self.obj.eval_var(var, **kwargs)
            except Exception as e:
                import sys
                raise type(e)(str(e) + ' -- error evaluating {var} with kwargs {kwargs}'.format(var=var, kwargs=kwargs)). \
                    with_traceback(sys.exc_info()[2])
            eq_(result, expected, '{var}(kwargs) -> {result!r} != {expected!r}'.format(
                var=var, kwargs=kwargs, result=result, expected=expected))

    def test_parser(self):
        # Same as the parser_input test
        strings = TestParsers.strings['input']
        from random import shuffle
        shuffle(strings)
        for string, expected in strings:
            result = self.obj.parse(string).asList()
            eq_(result, expected)

    @raises(NotImplementedError)
    def test_eval_string(self):
        self.obj.eval_string()