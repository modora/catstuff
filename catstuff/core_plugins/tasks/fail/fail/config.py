import os
from catstuff.tools.config import PluginConfig

_dir = os.path.dirname(__file__)
plugin_file = os.path.join(_dir, "../fail.plugin")
config = PluginConfig.from_path(plugin_file)

__version__= config.get('version', section='Documentation', default='1.0')
mod_name = config.get('name', section='Core')
build = config.get('build')