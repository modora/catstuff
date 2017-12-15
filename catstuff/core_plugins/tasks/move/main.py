from catstuff.core_plugins.tasks.move.config import mod_name, build
from catstuff.core import plugins
from catstuff import tools
import shutil


class Move(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, dest, **kwargs):
        src = tools.expandpath(path)
        dest = tools.expandpath(dest)

        return shutil.move(src, dest)