from datetime import datetime

from catstuff import core, tools
from catstuff.core.vars import CSVarPool
from .config import __version__, mod_name

class Parser(tools.argparser.CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('--config', help='path to config file',
                          default=tools.path.expandpath('~/.conf/catstuff.yml'))
        self.add_argument('-n', '--dry-run', action='store_true', default=False)
        self.add_argument('path')


class ImportVarPool(core.vars.VarPool):
    pool = {}


class Import(core.plugins.CSAction):
    mod_name = mod_name
    app = 'cs_import'
    parser = Parser()
    var_groups = [CSVarPool, ImportVarPool]

    def __init__(self):
        super().__init__(self.mod_name)
        self.config = CSVarPool.get('config', app='catstuff')
        self.import_settings = self.config.get(['plugins', 'actions', 'import'], {})
        self.manager = CSVarPool.get('manager', 'catstuff')
        self.db_driver = self.config.get(['db'], 'mongodb')

    def setup(self, args=None, namespace=None):
        """ Generates the variable space required for this action"""
        args = self.parser.parse_args(args=args, namespace=namespace)

        filelist = tools.path.import_file_list(args.path, **self.import_settings)

        var_group = core.vars.GroupVarPools(*self.var_groups, app=self.app)
        var_group.set('filelist', filelist)
        var_group.set('output', {})

    def execute_task(self, task):
        plugin = self.manager.getPluginByName(task, category="Plugins")
        if plugin is None:
            # TODO: log this instead of print
            print("No plugin with name {} was found, skipping".format(task))
            return

        base_settings = self.config.get(['plugins', 'tasks', task], {})
        local_settings = self.config.get(['tasks', task], {})
        task_settings = {**base_settings, **local_settings}

        try:
            output = plugin.plugin_object.main(**task_settings)
        except Exception:
            raise
        else:
            CSVarPool.get('output', app=self.app).update({task: output})

    def process_file(self, file):
        uid_gen_method = self.config.get(['plugins', 'db', self.db_driver, 'id'])
        master = core.dbs.CSMaster(uid_generate_method=uid_gen_method)
        master.path = file

        # TODO: Filter results of historic tasks
        historic_tasks = set()
        # historic_tasks = set(master.get({'_id': 0, 'path': 0}, eval_links=False, default={}).keys())
        pending_tasks = set(self.config.get(['tasks'], {}).keys()) - historic_tasks

        # tasks that already been executed

        # TODO: when group classification is working, we can do group level tasks

        master_data = self.execute_task_queue(pending_tasks)
        if master_data != {}:
            master.update(master_data)

    def execute_task_queue(self, queue):
        # if task fail, try again later. Continue this until all tasks have been executed or we encounter a
        # cyclic task execution

        master_data = {}
        while True:
            next_queue = set()

            for task in queue:
                try:
                    self.execute_task(task)
                except Exception:
                    next_queue.add(task)
                    status = 'failed'
                else:
                    status = 'up-to-date'
                finally:
                    master_data.update({
                        task: {
                            'last_updated': datetime.now().timestamp(),
                            'status'      : status,
                            'version'     : self.manager.getPluginByName(task, category="Plugins").version
                        }
                    })

            if next_queue is set():
                break
            elif set(queue) == set(next_queue):
                # TODO: log error
                print('Ran into cyclic tasks: {}'.format(queue))
                break
            queue = next_queue.copy()
            next_queue.clear()
        return master_data

    def main(self, *args):
        args = self.parser.parse_args(*args)
        self.setup(namespace=args)

        filelist = CSVarPool.get('filelist', self.app)

        if args.dry_run:
            for file in filelist:
                print(file)
            return

        tools.db.test_connection(core.dbs.CSMaster._default_conn)

        # TODO: classify groups

        for file in filelist:
            self.process_file(file)

