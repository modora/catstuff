class VarPool:
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

    def get_apps(self, var):
        """ Returns the set of apps in the var pool for a given variable"""
        return set(self.__dict.get(var, {}).keys())

    def get_all_apps(self):
        """ Returns the set of apps in the var pool for all variables"""
        return {var.keys() for var in self.__dict}

    def get_var_priority(self, var, app_list, default=...):
        """ Gets the value of a variable given a priority list of apps"""
        # Lower index values of app_list are given greater priority
        for app in app_list:
            try:
                return self.get(var, app=app)
            except KeyError:
                pass
        if default is ...:
            raise KeyError('{} is undefined in app_list'.format(var))
        else:
            return default