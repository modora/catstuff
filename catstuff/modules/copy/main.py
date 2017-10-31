import catstuff.tools.modules
import catstuff.tools.common
import os
import shutil

__dir__ = os.path.dirname(__file__)
__plugin_file__ = os.path.join(__dir__, "copy.plugin")
__version__ = catstuff.tools.modules.import_documentation(__plugin_file__).get('Version')

__mod__, __build__, _ = catstuff.tools.modules.import_core(__plugin_file__)


class Move(catstuff.tools.modules.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, path, dest, **kwargs):
        src = catstuff.tools.common.expandpath(path)
        dest = catstuff.tools.common.expandpath(dest)

        if os.path.isdir(path):
            return shutil.copytree(src, dest)
        return shutil.copy2(src, dest)