import catstuff.core.plugins
from catstuff.core_plugins.actions.plugins import mod_name
from catstuff.core_plugins.actions.plugins.parser import parser


class Commands(catstuff.core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = parser().parse_args(*args)
        args.func(args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()