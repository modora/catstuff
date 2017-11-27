import catstuff.tools.plugins
from catstuff.tools.common import import_file_list
from catstuff.core.tasks.filelist import mod_name, build


class Filelist(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, max_depth=0, followlinks=False,
             include=None, exclude=None, mode='whitelist',
             safe_walk=True, **kwargs):
        return import_file_list(
            path, max_depth=max_depth, followlinks=followlinks,
            include=include, exclude=exclude, mode=mode,
            safe_walk=safe_walk)
