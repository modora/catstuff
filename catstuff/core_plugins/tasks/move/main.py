import shutil

from catstuff import tools, core

from .config import mod_name, build


class Move(core.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = tools.path.expandpath(path)
        dest = tools.path.expandpath(dest)

        return shutil.move(src, dest)