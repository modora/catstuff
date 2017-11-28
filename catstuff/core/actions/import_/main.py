from catstuff import tools
from catstuff.tools.config import PluginConfig
from catstuff.core.actions.import_ import __version__, mod_name
from catstuff.core.manager import CSPluginManager
from datetime import datetime


class Parser(tools.argparser.CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('--config', help='path to config file',
                          default=tools.path.expandpath('~/.conf/catstuff.yml'))
        self.add_argument('-n', '--dry-run', action='store_true', default=False)
        self.add_argument('path')


class Import(tools.plugins.CSAction):
    def __init__(self):
        super().__init__(mod_name)

    @staticmethod
    def main(*args):
        parser = Parser()
        args = parser.parse_args(*args)

        try:
            config = tools.config.load_yaml(args.config)
        except FileNotFoundError:
            tools.path.touch(parser.get_default('config'))
            config = {}

        # TODO: classify groups

        group_list = [tools.vars.Vars, tools.vars.CSImportVars]

        tools.vars.GroupVarPools(*group_list, app='catstuff').set('manager', CSPluginManager())
        manager = group_list[0]().get('manager', 'catstuff')

        var_group = tools.vars.GroupVarPools(*group_list, app='cs_import')
        var_group.set('config', config)
        master_db = tools.config_parser.GlobalParser.master(config)
        var_group.set('master_db', master_db)

        filelist = tools.path.import_file_list(args.path, **tools.config_parser.GlobalParser.importer(config))
        var_group.set('filelist', filelist)

        var_group.set('output', {})

        if args.dry_run:
            for file in filelist:
                print(file)
            return

        master_coll = tools.db.Master(master_db)

        for file in filelist:
            tasks = tools.config_parser.LocalParser.tasks(config)

            # TODO: when group classification is working, we can do group level, local tasks
            master_coll.path = file
            # TODO: design a auto task scheduler
            for task in tasks:
                plugin = manager.getPluginByName(task, category="Plugins")
                if plugin is None:
                    print("No plugin with name {} was found, skipping".format(task))
                    continue
                plugin_config = PluginConfig.from_yapsy(plugin)

                name = plugin.name
                build = plugin_config.get('build')
                plugin_settings = tools.config_parser.LocalParser.plugins(config, name)

                try:
                    output = plugin.plugin_object.main(**plugin_settings)
                    status = 'up-to-date'
                    # group_list[0]().get(...) just gets the previous output results
                    var_group.set('output', group_list[0]().get('output', app=var_group.app, default={}).
                                  update({name: output}))
                except Exception as e:
                    # TODO: do some logging
                    from traceback import print_exc  # delete this when logging is done
                    print_exc()
                    status = 'failed'

                data = {
                    'status'      : status,
                    'last_updated': datetime.now().timestamp(),
                    'build'       : build
                }

                master_coll.update({'.'.join([name, key]): value for key, value in data})


if __name__ == '__main__':
    Import().main()