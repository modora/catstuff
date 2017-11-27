import catstuff.tools.plugins
import catstuff.tools.common
import shutil
import os
from catstuff.core.tasks.copy import mod_name, build


class Move(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = catstuff.tools.common.expandpath(path)
        dest = catstuff.tools.common.expandpath(dest)

        if os.path.isdir(path):
            return shutil.copytree(src, dest)
        return shutil.copy2(src, dest)
