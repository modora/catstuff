import catstuff.core.plugins
from catstuff.core_plugins.actions.version.parser import Parser
from catstuff.core_plugins.actions.version import mod_name


class Version(catstuff.core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = Parser().parse_args(*args)
        args.func(args)


if __name__ == '__main__':
    Version.main()