import datetime
import os

import pymongo

import catstuff.tools.common
import catstuff.tools.config
import catstuff.tools.db
import catstuff.tools.plugins
from catstuff.core import plugin_manager
from catstuff.core.import_ import core_logger

_dir = os.path.dirname(os.path.realpath(__file__))

# logging.basicConfig(level=logging.DEBUG)


_restricted_plugin_names = {'path'}

manager = plugin_manager.manager
logger = core_logger.logger


def main(filepath, config={}):
    output = {}  # output of plugin main
    tasks = config['tasks']

    manager.collectPlugins()

    (_master_host, _master_port, _master_name) = \
        catstuff.tools.config.get_db_settings( config, default_db=pymongo.MongoClient().catstuff)
    master_db = pymongo.MongoClient(host=_master_host, port=_master_port)[_master_name]
    master = catstuff.tools.db.Master(db=master_db)

    for task in tasks:
        plugin = manager.getPluginByName(task, category="Plugins")
        if plugin is None:
            print("No plugin with name {} was found, skipping".format(task))
            continue
        name = plugin.name
        build = plugin.details.sections.Core.build
        if name in _restricted_plugin_names:
            raise NameError("Plugin name {} is forbidden, rename it!!".format(name))

        try:
            task_settings = config['plugins'][task]
            task_settings = {} if task_settings is None else task_settings
        except KeyError:
            core_logger.debug('No settings found in config for task {}, assuming defaults'.format(task))
            task_settings = {}

        try:
            # insert attribute in plugin
            plugin._config = config
            plugin._output = output

            output[name] = plugin.plugin_object.main(**task_settings)
            status = 'present'
        except Exception as e:
            core_logger.error("Failed to execute {}:".format(name), exc_info=True)
            status = 'failed'

        data = {
            'status': status,
            'last_updated': datetime.datetime.now().timestamp(),
            'build': build
        }
        master.update({(name+key): data[key] for key in data})  # add data to

if __name__ == '__main__':
    main('fakepath', config={'tasks': ['checksum']})