import catstuff.tools.plugins
from catstuff.core.actions.commands import mod_name
from catstuff.core.actions.commands.parser import Parser


class Commands(catstuff.tools.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = Parser().parse_args(*args)  # leaving args unused as a placeholder for the future
        args.func(args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()