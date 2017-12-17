from catstuff import core

from .parser import Parser
from .config import mod_name


class Commands(core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = Parser().parse_args(*args)  # leaving args unused as a placeholder for the future
        args.func(args)
