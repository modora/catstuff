# import catstuff.core.plugins
# import os
#
# __dir__ = os.path.dirname(__file__)
# __plugin_file__ =  os.path.join(__dir__, "replaygain.plugin")  # name of modname file
# __version__ = catstuff.core.plugins.import_documentation(__plugin_file__).get('Version')
#
# __mod__, __build__, _ = catstuff.core.plugins.import_core(__plugin_file__)
#
#
# class ReplayGain(catstuff.core.plugins.CSTask):  # Rename the class
#     def __init__(self):
#         super().__init__(__mod__, __build__)
#
#     def main(self):
#         return
