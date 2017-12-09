class VarPool:
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

    @classmethod
    def get(cls, var, app=None, default=...):
        app_vars = cls.pool.get(var, {})
        if app:
            return app_vars[app] if default is ... else app_vars.get(app, default)
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
    def reset(cls):
        """ Removes all variables in the pool"""
        cls.pool = {}

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
