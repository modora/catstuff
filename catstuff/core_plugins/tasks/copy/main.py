import os
import shutil

from catstuff import tools
from catstuff.core import plugins
from catstuff.core_plugins.tasks.copy.config import mod_name, build


class Move(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = tools.expandpath(path)
        dest = tools.expandpath(dest)

        if os.path.isdir(path):
            return shutil.copytree(src, dest)
        return shutil.copy2(src, dest)
