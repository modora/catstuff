# import datetime
# import os
#
# from catstuff.tools.common import import_file_list
# from catstuff.tools.config import try_get
# import catstuff.config.master
# import catstuff.tools.db
# from catstuff.core.manager import PluginManager
# from catstuff.tools.argparser import CSArgParser
#
# _dir = os.path.dirname(os.path.realpath(__file__))
# __version__ = os.
#
# # logging.basicConfig(level=logging.DEBUG)
#
#
# _restricted_plugin_names = {'path'}
#
#
# class Parser(CSArgParser):
#     def __init__(self):
#         super().__init__()
#         self.add_argument('--version', action=version, version=)
#
#
#
# def main(*args):
#     parser = Parser()
#     args = parser.parse_args(*args)
#
#     config = args.config
#
#
#     if config is None:
#         config = {}
#     assert isinstance(config, dict)
#
#     output = {}  # output of plugin main
#     tasks = config.get('tasks', {})
#
#     master_db = catstuff.config.master.parser(config)
#
#     filelist = import_file_list(path)
#
#     master = catstuff.tools.db.Master(db=master_db)
#
#     for file in filelist:
#         for task in tasks:
#             plugin = manager.getPluginByName(task, category="Plugins")
#             if plugin is None:
#                 print("No plugin with name {} was found, skipping".format(task))
#                 continue
#             name = plugin.name
#             build = plugin.details.sections.Core.build
#             if name in _restricted_plugin_names:
#                 raise NameError("Plugin name {} is forbidden, rename it!!".format(name))
#
#             task_settings = try_get(config, )
#             try:
#                 task_settings = config['plugins'][task]
#                 task_settings = {} if task_settings is None else task_settings
#             except KeyError:
#                 # logger.debug('No settings found in config for task {}, assuming defaults'.format(task))
#                 task_settings = {}
#
#             try:
#                 # insert attribute in plugin
#                 plugin._config = config
#                 plugin._output = output
#                 plugin._file = file
#
#                 output[name] = plugin.plugin_object.main(**task_settings)
#                 status = 'present'
#             except Exception as e:
#                 # logger.error("Failed to execute {}:".format(name), exc_info=True)
#                 status = 'failed'
#
#             data = {
#                 'status': status,
#                 'last_updated': datetime.datetime.now().timestamp(),
#                 'build': build
#             }
#             master.update({(name+key): data[key] for key in data})  # add data to
#
#
# if __name__ == '__main__':
#     main()