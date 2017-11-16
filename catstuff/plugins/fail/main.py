import catstuff.tools.plugins
import os

_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "fail.plugin")
__version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')

_mod, _build, _ = catstuff.tools.plugins.import_core(_plugin_file)


class Fail(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(_mod, _build)

    def main(self, *args, **kwargs):
        raise NotImplementedError("Fail module has failed correctly!!")


if __name__ == '__main__':
    Fail().main()