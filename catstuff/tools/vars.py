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

Usage:
To access the global catstuff variables, import the Vars class into your module
Then init

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

    def get(self, var , app=None, default=...):
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