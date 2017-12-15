from catstuff.core import plugins
from catstuff.core_plugins.actions.strmethods.config import mod_name, __version__
from catstuff.core_plugins.actions.strmethods.parser import Parser


class StrMethods(plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):  # modify anything below here
        args = Parser().parse_args(*args)
        args.func(args)


if __name__ == '__main__':
    StrMethods.main()
