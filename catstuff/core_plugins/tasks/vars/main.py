from catstuff.core_plugins.tasks.vars import mod_name, build
from catstuff.tools import plugins
from catstuff import tools


class Vars(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    @staticmethod
    def parse(**kwargs):
        keywords = {'pools': {'name': None, 'app': 'vars'}}

        vars_ = kwargs.copy()
        settings = {}
        for key, default in keywords:
            settings[key] = vars_.pop(key, default=default)
        return vars_, settings

    def main(self, **kwargs):  # must have **kwargs as input

        pools = []  # TODO: currently, defining pools is unsupported
        # TODO: currently, specifying the app name is unsupported
        var_pool = tools.vars.GroupVarPools(tools.vars.VarPool, *pools, app=mod_name)
        for name, value in kwargs.items():
            var_pool.set(name, value)
        return
