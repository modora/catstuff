import os
from catstuff.tools.config import PluginConfig

_dir = os.path.dirname(os.path.realpath(__file__))
plugin_file = os.path.join(_dir, "../version.plugin")
config = PluginConfig.from_path(plugin_file)

__version__ = config.get('version', section='Documentation', default='0.0')
mod_name = config.get('name', section='Core')
