import catstuff.tools.plugins
from catstuff.core.tasks.vars import mod_name, build

class VarContainer:
    pass


class Vars(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    @staticmethod
    def init():
        global VarContainer

    def main(self, **kwargs):  # must have **kwargs as input
        raise NotImplementedError
        for var in kwargs:
            setattr(VarContainer, var, kwargs[var])
        return
