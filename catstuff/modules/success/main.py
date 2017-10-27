import catstuff.tools.modules as mods
# from catstuff.tools.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.importCore(os.path.join(__dir__, "success.plugin"))


class Success(mods.CSCollection):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, **kwargs):
        print("Success")
        return "Success"


if __name__ == '__main__':
    print(Success().main())
