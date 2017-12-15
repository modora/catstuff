import catstuff.core.plugins
from catstuff.core_plugins.actions.commands.parser import Parser
from catstuff.core_plugins.actions.commands.config import mod_name


class Commands(catstuff.core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = Parser().parse_args(*args)  # leaving args unused as a placeholder for the future
        args.func(args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()