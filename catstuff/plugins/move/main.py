import catstuff.tools.modules
import catstuff.tools.common
import os
import shutil

_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "move.plugin")
__version__ = catstuff.tools.modules.import_documentation(_plugin_file).get('Version')

_mod, _build, _ = catstuff.tools.modules.import_core(_plugin_file)


class Move(catstuff.tools.modules.CSModule):
    def __init__(self):
        super().__init__(_mod, _build)

    def main(self, path, dest, **kwargs):
        src = catstuff.tools.common.expandpath(path)
        dest = catstuff.tools.common.expandpath(dest)

        return shutil.move(src, dest)