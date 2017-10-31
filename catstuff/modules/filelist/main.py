from catstuff.tools.common import import_file_list
import catstuff.tools.modules as mods
# from catstuff.tools.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.import_core(os.path.join(__dir__, "filelist.plugin"))


class Filelist(mods.CSCollection):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, path, max_depth=0, followlinks=False,
             include=None, exclude=None, mode='whitelist',
             safe_walk=True, **kwargs):
        return import_file_list(
            path, max_depth=max_depth, followlinks=followlinks,
            include=include, exclude=exclude, mode=mode,
            safe_walk=safe_walk)