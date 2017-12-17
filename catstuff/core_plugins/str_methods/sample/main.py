from catstuff.core import plugins
from catstuff.core_plugins.str_methods.sample.config import __version__


class Sample(plugins.StrMethod):
    def foo(self):
        """ Returns 'bar'"""
        return 'bar'

    def hello(self):
        """ Returns 'world' """
        return 'world'

    def lorem(self):
        """ Returns 'ipsum' """
        return 'ipsum'

    def ping(self):
        """ Returns 'pong' """
        return 'pong'

    def one(self):
        """ Returns the integer 1"""
        return 1

    def two(self):
        """ Returns the integer 2"""
        return 2

    def args(self, *args):
        """ Returns the list of arguments entered"""
        return args

    def reverse(self):
        """ Reverses the contents of a string"""
        return self[::-1]
