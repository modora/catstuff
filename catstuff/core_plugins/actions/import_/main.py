from datetime import datetime

from catstuff import tools
from catstuff.core import CSMaster
from catstuff.core_plugins.actions.import_ import __version__, mod_name
from catstuff.tools.config import PluginConfig


class Parser(tools.argparser.CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('--config', help='path to config file',
                          default=tools.path.expandpath('~/.conf/catstuff.yml'))
        self.add_argument('-n', '--dry-run', action='store_true', default=False)
        self.add_argument('path')


class CSImportVarPool(tools.vars.VarPool):
    pass


class Import(tools.plugins.CSAction):
    mod_name = mod_name
    app = 'cs_import'
    parser = Parser()
    var_groups = {tools.vars.VarPool, CSImportVarPool}

    def __init__(self):
        super().__init__(self.mod_name)

    def setup(self, args=None, namespace=None):
        """ Generates the variable space required for this action"""
        args = self.parser.parse_args(args=args, namespace=namespace)

        try:
            config = tools.config.load_yaml(args.config)
        except FileNotFoundError:
            tools.path.touch(self.parser.get_default('config'))
            config = {}
        config = tools.config_parser._Config(config)  # allows monkey patching of dicts
        config.globals = tools.config_parser.GlobalParser.parse(config)

        filelist = tools.path.import_file_list(args.path, **config.globals.importer)

        var_group = tools.vars.GroupVarPools(*self.var_groups, app=self.app)
        var_group.set('config', config)
        var_group.set('mongo_client', config.globals.mongo_client)
        var_group.set('mongo_db', config.globals.mongo_db)
        var_group.set('filelist', filelist)
        var_group.set('output', {})

    def main(self, *args):
        args = self.parser.parse_args(*args)
        self.setup(namespace=args)

        # TODO: classify groups

        vars_ = CSImportVarPool()

        manager = tools.vars.VarPool().get('manager', 'catstuff')
        master_coll = CSMaster(vars_.get('mongo_db', self.app))
        filelist = vars_.get('filelist', self.app)
        config = vars_.get('config')

        if args.dry_run:
            for file in filelist:
                print(file)
            return

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
                    vars_.set('output', vars_.get('output', app=self.app, default={}).
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