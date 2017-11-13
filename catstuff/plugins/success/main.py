import catstuff.tools.plugins
# from catstuff.tools.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os

_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "success.plugin")
__version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')

_mod, _build, _ = catstuff.tools.plugins.import_core(_plugin_file)


class Success(catstuff.tools.plugins.CSModule):
    def __init__(self):
        super().__init__(_mod, _build)

    def main(self, **kwargs):
        print("Success")
        return "Success"


if __name__ == '__main__':
    print(Success().main())
