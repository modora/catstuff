from catstuff import core

from .parser import Parser
from .config import mod_name


class Version(core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = Parser().parse_args(*args)
        args.func(args)
