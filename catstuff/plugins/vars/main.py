# import catstuff.tools.plugins
# import os
#
# _dir = os.path.dirname(__file__)
# _plugin_file = os.path.join(_dir, "vars.plugin")  # name of modname file
# __version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')
#
# _mod, _build, _ = catstuff.tools.plugins.import_core(_plugin_file)
#
#
# class Vars(catstuff.tools.plugins.CSTask):
#     def __init__(self):
#         super().__init__(_mod, _build)
#
#     def main(self, **kwargs):  # must have **kwargs as input
#         raise NotImplementedError('vars mod not implemented')
#         super().main(**kwargs)  # sample code -- delete this
#         return
