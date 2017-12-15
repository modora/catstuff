from catstuff import core
from .config import mod_name, build


class Fail(core.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, *args, **kwargs):
        raise NotImplementedError("Fail task has successfully executed!!")
