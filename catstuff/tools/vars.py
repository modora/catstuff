# Container for module variables

'''
Variables are contained in a private variable of the class Vars. The dictionary
has a structure in this form

Vars: {
    'var_name1': {
        app1: value,
        app2: value,
        app3: value, ...
    }
}

Helper functions have been put into place to modify this structure

You can create your own inter-module variable pool by subclassing Vars

Usage:
To access the global catstuff variables, import the Vars class into your module and init the class
    from catstuff.tools.vars import Vars

    cs_vars = Vars()

At this point, you can get any variable contained within the class by
    cs_vars.get(var_name, app_name)
If the app_name is None, then this returns a dictionary of all applications
that have saved a variable with var_name

To get a copy of all saved variables, use the dump command
    cs_vars.dump()
To get all variables of a specific application, use the get_app_vars command
    cs_vars.get_app_vars('app_name')

To add a variable and delete a variable, you will need to specify an application name during initilization
    cs_vars = Vars('app_name')
Use the set command to set a new variable and the delete command to delete a variable
    cs_vars.set('var1', 'value1')
    cs_vars.set('var2', 'value2')

    cs_vars.delete('var1')

To create your own global variable pool, subclass Vars like so
    class MyVarPool_1(Vars):
        pass

    class MyVarPool_2(Vars):
        pass

    cs_vars = Vars()
    my_var_pool_1 = MyVarPool_1()
    my_var_pool_2 = MyVarPool_2()

All three of the variable pools can operate independently of each other!

You can support multiple variable pools easily by forming a group-pool
    my_group = GroupVarPools(Vars, MyVarPool_1, MyVarPool_2)
We can now act on all three pool simultaneously using the same commands

'''


class Vars:
    __dict = {}

    def __init__(self, app=None):
        self._app = app

    @property
    def app(self):
        if self._app:
            return self._app
        else:
            raise AttributeError('App name not set')

    def set(self, var, value):
        try:
            self.__dict[var].update({
                self.app: value
            })
        except KeyError:
            self.__dict[var] = {self.app: value}

    def get(self, var, app=None, default=...):
        app_vars = self.__dict.get(var, {})
        if app:
            return app_vars[app] if default is ... else app_vars.get(app, default)
        else:
            return app_vars

    def delete(self, var):
        try:
            del self.__dict.get(var, {})[self.app]
            if self.__dict[var] is {}:  # cleanup empty dicts
                del self.__dict[var]
        except KeyError:
            pass

    def dump(self):
        """ Returns a copy of all variables"""
        return self.__dict.copy()

    def get_app_vars(self, app: str):
        """ Returns a dictionary of all variables set by some app"""
        d = {}
        for var in self.__dict:
            try:
                d.update({var: self.get(var, app)})
            except KeyError:
                pass
        return d


class CSImportVars(Vars):
    pass


class GroupVarPools:
    def __init__(self, *pools, app=None):
        if not all([isinstance(pool, Vars) for pool in pools]):
            raise TypeError('Invalid var pool specified')
        self.pools = {pool(app) for pool in pools}
        self._app = app

    def add_pool(self, *pools):
        if not all([isinstance(pool, Vars) for pool in pools]):
            raise TypeError('Invalid var pool specified')
        self.pools.update(pools)

    def remove_pool(self, *pools):
        if not all([isinstance(pool, Vars) for pool in pools]):
            raise TypeError('Invalid var pool specified')
        self.pools.difference_update(pools)

    @property
    def app(self):
        if self._app:
            return self._app
        else:
            raise AttributeError('App name not set')

    def set(self, var, value):
        for pool in self.pools:
            pool.set(var, value)

    def get(self, var, app=None, default=..., skip_missing=False):
        if skip_missing:
            d = {}
            try:
                d.update({pool.__class__.__name__:
                              pool.get(var, app=app, default=default)
                          for pool in self.pools
                          })
            except KeyError:
                pass
            return d
        else:
            return {pool.__class__.__name__: pool.get(var, app=app, default=default)
                    for pool in self.pools}

    def delete(self, var):
        for pool in self.pools:
            pool(app=self.app).delete(var)

    def dump(self):
        """ Returns a copy of all variables"""
        return {pool.__class__.__name__: pool.dump() for pool in self.pools}

    def get_app_vars(self, app: str):
        """ Returns a dictionary of all variables set by some app"""
        return {pool.__class__.__name__: pool.get_app_vars(app) for pool in self.pools}
