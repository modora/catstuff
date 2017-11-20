import catstuff.tools.plugins
from catstuff.tools.common import expandpath
import shutil
from catstuff.core.tasks.move import mod_name, build


class Move(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = expandpath(path)
        dest = expandpath(dest)

        return shutil.move(src, dest)