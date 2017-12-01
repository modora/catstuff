from tests.common import *
from catstuff.core.str_formatter import *
import inspect

class TestConstructor(StrFormatter):
    def test_func(self):
        CSStr = CSStrConstructor()
        ok_(str in inspect.getmro(CSStr), 'str not in CSStr base class')
        ok_(CSStr is not str, 'str not a subclass of CSStr')
        ok_(isinstance(CSStr('test str'), str), 'testing with an actual string failed')


class TestCSStrFuncs(StrFormatter):
    def setup(self):
        super().setup()
        self.CSStr = CSStrConstructor()

    def test_basic(self):
        s = 'literal string'
        s = self.CSStr(s)

        try:
            eq_(s.reverse(), s[::-1])
        except AttributeError:
            print('Random plugin for StrFormat not found, aborting test')


class TestFormatter(StrFormatter):
    def setup(self):
        super().setup()
        self.CSStr = CSStrConstructor()
