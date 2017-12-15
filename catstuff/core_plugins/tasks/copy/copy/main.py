import os
import shutil

from catstuff import tools, core

from .config import mod_name, build


class Copy(core.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = tools.path.expandpath(path)
        dest = tools.path.expandpath(dest)

        if os.path.isdir(path):
            return shutil.copytree(src, dest)
        return shutil.copy2(src, dest)
