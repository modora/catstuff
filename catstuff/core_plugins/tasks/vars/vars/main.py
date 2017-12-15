from .config import mod_name, build
from catstuff import core


class Vars(core.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    @staticmethod
    def config_parser():
        raise NotImplementedError

    def main(self):
        raise NotImplementedError
