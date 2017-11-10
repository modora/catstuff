import catstuff.tools.modules
import os

__dir__ = os.path.dirname(__file__)
__plugin_file__ =  os.path.join(__dir__, "replaygain.plugin")  # name of modname file
__version__ = catstuff.tools.modules.import_documentation(__plugin_file__).get('Version')

__mod__, __build__, _ = catstuff.tools.modules.import_core(__plugin_file__)


class ReplayGain(catstuff.tools.modules.CSModule):  # Rename the class
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self):
        return
