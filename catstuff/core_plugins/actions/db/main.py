from catstuff import core, tools
from .config import mod_name


class Template(core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main():  # modify anything below here
        args = Parser().parse_args()
        print(args.args)

