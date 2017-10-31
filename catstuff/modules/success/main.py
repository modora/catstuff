import catstuff.tools.modules
# from catstuff.tools.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os

__dir__ = os.path.dirname(os.path.realpath(__file__))
__mod__, __build__, _ = catstuff.tools.modules.import_core(os.path.join(__dir__, "success.plugin"))


class Success(catstuff.tools.modules.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, **kwargs):
        print("Success")
        return "Success"


if __name__ == '__main__':
    print(Success().main())
