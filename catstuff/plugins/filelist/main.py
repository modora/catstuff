# from catstuff.tools.common import import_file_list
# import catstuff.tools.plugins
# # from catstuff.tools.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
# import os
#
# _dir = os.path.dirname(__file__)
# _plugin_file = os.path.join(_dir, "filelist.plugin")
# __version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')
#
# _mod, _build, _ = catstuff.tools.plugins.import_core(_plugin_file)
#
#
# class Filelist(catstuff.tools.plugins.CSTask):
#     def __init__(self):
#         super().__init__(_mod, _build)
#
#     def main(self, path, max_depth=0, followlinks=False,
#              include=None, exclude=None, mode='whitelist',
#              safe_walk=True, **kwargs):
#         return import_file_list(
#             path, max_depth=max_depth, followlinks=followlinks,
#             include=include, exclude=exclude, mode=mode,
#             safe_walk=safe_walk)