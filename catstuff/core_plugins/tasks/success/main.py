from .config import mod_name, build
from catstuff import core


class Success(core.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, **kwargs):
        msg = "Success"
        print(msg)
        return msg
