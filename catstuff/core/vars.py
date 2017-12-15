"""
Variables are contained in a private variable of the class Vars. The dictionary
has a structure in this form

vars = {
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
    from catstuff.tools.vars import VarPool

At this point, you can get any variable contained within the class by
    VarPool.get(var_name, app_name)
If the app_name is None, then this returns a dictionary of all applications
that have saved a variable with var_name

To get a copy of all saved variables, use the dump command
    VarPool.dump()
To get all variables of a specific application, use the get_app_vars command
    VarPool.get_app_vars(app_name)

To add a variable and delete a variable, you will need to specify an application name during initilization
    cs_vars = VarPool(app_name)
Use the set command to set a new variable and the delete command to delete a variable
    cs_vars.set('var1', 'value1')
    cs_vars.set('var2', 'value2')

    cs_vars.delete('var1')

To create your own global variable pool, subclass Vars like so
    class MyVarPool_1(VarPool):
        pass

    class MyVarPool_2(VarPool):
        pool = {}

    cs_vars = Vars
    my_var_pool_1 = MyVarPool_1()
    my_var_pool_2 = MyVarPool_2()

MyVarPool_1 is directed connected to the VarPool meaning that any pool modifications
in MyVarPool_1 will also occur in VarPool. More importantly, this allows for method
extensions for VarPool. To make a completely independent VarPool, replace the class
attribute with an empty dictionary.
If you want to set up default key/values

You can support multiple variable pools easily by forming a group-pool
    my_group = GroupVarPools(Vars, MyVarPool_1, MyVarPool_2)
    my_group2 = GroupVarPools(cs_vars, my_var_pool_1, my_var_pool_1)
We can now act on all three pool simultaneously using the same commands

Other methods included are:
    get_app_vars
    get_apps
    get_all_apps
    get_var_priority
Use the __doc__ attribute to see a description for each
"""

import inspect
import catstuff.core


class VarPool:
    # Reinit this variable to make pool independent (check independence using id())
    # admittedly, a defaultdict would be easier to implement but slightly more work for the developer
    # abiet, it's only two lines of code to add but the dev would have to know what a default dict is
    pool = {}

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
            self.pool[var].update({
                self.app: value
            })
        except KeyError:
            self.pool[var] = {self.app: value}

    def set_many(self, data: dict):
        """ Convenience method for setting many variables at once"""
        for var, value in data.items():
            self.set(var, value)

    @classmethod
    def get(cls, var, app=None, default=...):
        app_vars = cls.pool.get(var, {})
        if app:
            try:
                return app_vars[app] if default is ... else app_vars.get(app, default)
            except KeyError:
                raise KeyError("No app named '{app}' found in variable '{var}' in '{pool}'".format(
                    app=app, var=var, pool=cls.__name__
                ))
        else:
            return app_vars

    def delete(self, var):
        """ Deletes a variable set by app, requires instance to be that app"""
        try:
            del self.pool.get(var, {})[self.app]
            if self.pool[var] is {}:  # cleanup empty dicts
                del self.pool[var]
        except KeyError:
            pass

    @classmethod
    def clear(cls):
        """ Removes all variables in the pool"""
        cls.pool.clear()

    @classmethod
    def dump(cls):
        """ Returns a copy of all variables"""
        return cls.pool.copy()

    @classmethod
    def get_app_vars(cls, app: str):
        """ Returns a dictionary of all variables set by some app"""
        d = {}
        for var in cls.pool:
            try:
                d.update({var: cls.get(var, app)})
            except KeyError:
                pass
        return d

    @classmethod
    def get_apps(cls, var):
        """ Returns the set of apps in the var pool for a given variable"""
        return set(cls.pool.get(var, {}).keys())

    @classmethod
    def get_all_apps(cls):
        """ Returns the set of apps in the var pool for all variables"""
        return {var.keys() for var in cls.pool}

    @classmethod
    def get_var_priority(cls, var, app_list, default=...):
        """ Gets the value of a variable given a priority list of apps"""
        # Lower index values of app_list are given greater priority
        for app in app_list:
            try:
                return cls.get(var, app=app)
            except KeyError:
                pass
        if default is ...:
            raise KeyError('{} is undefined in app_list'.format(var))
        else:
            return default


class CSVarPool(VarPool):
    @classmethod
    def setup(cls, data=..., app='catstuff'):
        from catstuff.core import plugins

        if data is ...:  # default setup data

            data = {
                'varpool': cls,
                'manager': plugins.CSPluginManager(),
            }
        for var, value in data.items():
            cls(app=app).set(var, value)


class GroupVarPools:
    def __init__(self, *pools, app=None):
        self._app = app
        self.pools = self.__check_pools(*pools)

    def add_pool(self, *pools):
        self.pools.update(self.__check_pools(*pools))

    def remove_pool(self, *pools):
        self.pools.difference_update(self.__check_pools(*pools))

    def __check_pools(self, *pools):
        """ Checks if all pools are Var pools and returns the set of pools"""
        if not all([VarPool in (inspect.getmro(pool) if type(pool) is type else pool.mro())
                    for pool in pools]):
            raise TypeError('Invalid var pool specified')
        return {pool(self.app) if type(pool) is type else pool for pool in pools}

    @property
    def app(self):
        return self._app

    def set(self, var, value):
        for pool in self.pools:
            pool.set(var, value)

    def get(self, var, app=None, default=..., skip_missing=False):
        if skip_missing:
            d = {}
            for pool in self.pools:
                try:
                    d.update({pool.__class__.__name__: pool.get(var, app=app, default=default)})
                except KeyError:
                    pass
            return d
        else:
            return {pool.__class__.__name__: pool.get(var, app=app, default=default)
                    for pool in self.pools}

    def clear(self, var):
        for pool in self.pools:
            pool(app=self.app).clear(var)

    def dump(self):
        """ Returns a copy of all variables"""
        return {pool.__class__.__name__: pool.dump() for pool in self.pools}

    def get_app_vars(self, app: str):
        """ Returns a dictionary of all variables set by some app"""
        return {pool.__class__.__name__: pool.get_app_vars(app) for pool in self.pools}

    def get_apps(self, var):
        """ Returns the set of apps in the var pool for a given variable"""
        return {pool.__class__.__name__: pool.get_apps(var) for pool in self.pools}

    def get_all_apps(self):
        """ Returns the set of apps in the var pool for all variables"""
        return {pool.__class__.__name__: pool.get_all_apps() for pool in self.pools}

    def get_var_priority(self, *args, skip_missing=False, **kwargs):
        """ Gets the value of a variable given a priority list of apps"""
        if skip_missing:
            d = {}
            for pool in self.pools:
                try:
                    d.update({pool.__class__.__name__: pool.get_var_priority(*args, **kwargs)})
                except KeyError:
                    pass
            return d
        else:
            return {pool.__class__.__name__: pool.get_var_priority(*args, **kwargs) for pool in self.pools}
