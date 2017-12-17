from catstuff.core import plugins
from .config import mod_name, __version__
from .parser import Parser


class StrMethods(plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):  # modify anything below here
        args = Parser().parse_args(*args)
        args.func(args)
