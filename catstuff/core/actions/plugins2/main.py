import catstuff.tools.plugins
import catstuff.core.actions.plugins2.parser
parser = catstuff.core.actions.plugins2.parser.parser
import catstuff.core.actions.plugins2

mod_name = catstuff.core.actions.plugins2.mod_name

class Commands(catstuff.tools.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = parser.parse_args(*args)
        args.func(args)


if __name__ == '__main__':
    commands = Commands()
    commands.main()