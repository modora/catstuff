import catstuff.tools.plugins
# from catstuff.tools.plugins import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os
from catstuff.tools.config import PluginConfig


_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "success.plugin")

config = PluginConfig.from_path(_plugin_file)
__version__ = config.get('version', section='Documentation', default='0.0')
mod_name = config.get('name', section='Core')
build = config.get('build', section='Core', default=1)


class Success(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, **kwargs):
        msg = "Success"
        print(msg)
        return msg


if __name__ == '__main__':
    print(Success().main())
