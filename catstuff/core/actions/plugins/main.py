import catstuff.tools.plugins
from catstuff.core.actions.plugins.parser import parser
from catstuff.core.actions.plugins import mod_name


class Commands(catstuff.tools.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = parser().parse_args(*args)
        args.func(args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()