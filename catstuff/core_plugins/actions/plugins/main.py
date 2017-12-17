from catstuff import core
from .config import mod_name
from .parser import parser


class Plugins(core.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        args = parser().parse_args(*args)
        args.func(args)
