import catstuff.tools.plugins
import catstuff.tools.common
import os
import shutil

_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "copy.plugin")
__version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')

_mod, _build, _ = catstuff.tools.plugins.import_core(_plugin_file)


class Move(catstuff.tools.plugins.CSModule):
    def __init__(self):
        super().__init__(_mod, _build)

    def main(self, path, dest, **kwargs):
        src = catstuff.tools.common.expandpath(path)
        dest = catstuff.tools.common.expandpath(dest)

        if os.path.isdir(path):
            return shutil.copytree(src, dest)
        return shutil.copy2(src, dest)