import catstuff.toolbox.modules as mods
# from catstuff.toolbox.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.importCore(os.path.join(__dir__, "fail.plugin"))


class Fail(mods.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, *args, **kwargs):
        raise NotImplementedError("Fail module has failed correctly!!")


if __name__ == '__main__':
    Fail().main()