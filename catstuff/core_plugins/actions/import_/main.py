from datetime import datetime

from catstuff import core, tools

from .config import __version__, mod_name


class Parser(tools.argparser.CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('--config', help='path to config file',
                          default=tools.path.expandpath('~/.conf/catstuff.yml'))
        self.add_argument('-n', '--dry-run', action='store_true', default=False)
        self.add_argument('path')


class CSImportVarPool(core.vars.VarPool):
    pool = {}


class Import(core.plugins.CSAction):
    mod_name = mod_name
    app = 'cs_import'
    parser = Parser()
    var_groups = [core.vars.CSVarPool, CSImportVarPool]

    def __init__(self):
        super().__init__(self.mod_name)

    def setup(self, args=None, namespace=None):
        """ Generates the variable space required for this action"""
        args = self.parser.parse_args(args=args, namespace=namespace)

        config = core.vars.CSVarPool.get('config', app='catstuff')

        filelist = tools.path.import_file_list(args.path, **config.globals.importer)

        var_group = core.vars.GroupVarPools(*self.var_groups, app=self.app)
        var_group.set('config', config)
        var_group.set('filelist', filelist)
        var_group.set('output', [])

    def main(self, *args):
        # TODO: Rewrite this

        args = self.parser.parse_args(*args)
        self.setup(namespace=args)

        # TODO: classify groups

        vars_ = CSImportVarPool()

        manager = core.vars.CSVarPool.get('manager', 'catstuff')
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
