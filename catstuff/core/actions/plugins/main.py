import catstuff.tools.plugins
from catstuff.core.actions.plugins import mod_name
from catstuff.core.actions.plugins.parser import parser
from catstuff.core.actions.plugins.formatter import print_info


class Commands(catstuff.tools.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = parser.parse_args(*args)  # leaving args unused as a placeholder for the future

        print_info(args.args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()