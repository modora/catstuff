from catstuff.core_plugins.tasks.fail.config import mod_name, build
from catstuff.core import plugins
from catstuff import tools


class Filelist(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, path, max_depth=0, followlinks=False,
             include=None, exclude=None, mode='whitelist',
             safe_walk=True, **kwargs):
        return tools.import_file_list(
            path, max_depth=max_depth, followlinks=followlinks,
            include=include, exclude=exclude, mode=mode,
            safe_walk=safe_walk)
