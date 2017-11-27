from yapsy.IPlugin import IPlugin
from catstuff.tools.db import property_getter, Collection, Master


class StrMethod(str):
    """ Base method to add to the CSStr class"""
    '''
    To avoid collisions with other plugins, use the python name mangling '__attr' 
    with double underscores for private variables. Additionally, name your subclass
    the name of your plugin (underscore separated)
    '''

    pass


class _CSPluginTemplate:
    """ Template for most catstuff plugin classes"""
    def __init__(self, name):
        super().__init__()
        self.name = name

    def main(self, *args, **kwargs):
        print("Executed main method of '{name}' plugin of class '{cls}'".format(
            name=self.name, cls=self.__class__.__name__))


class CSAction(_CSPluginTemplate):
    """ Create a catstuff action"""
    def __init__(self, name):
        super().__init__(name)

    def main(self, *args):
        super().main()


class CSTask(_CSPluginTemplate):
    """ Create a catstuff task"""
    def __init__(self, name, build):
        super().__init__(name)
        self.build = build

    @property
    def config(self):
        return property_getter(self, "_config", default={})

    @property
    def output(self):
        return property_getter(self, "_output", default={})


class CSCollection(Collection, CSTask):
    """ Create a catstuff task with built-in mongodb api"""
    def __init__(self, name, build, path='', database=None, master_db=None):
        Collection.__init__(self, name, db=database)
        CSTask.__init__(self, name, build)

        self.master = Master(db=(master_db or self._default_db))
        self.path = path

    @property
    def uid(self):
        return property_getter(self, '_uid', default=self.generate_uid())

    @uid.setter
    def uid(self, value):
        Collection.uid.fset(self, value)  # this is correct -- warnings are wrong

        if 'inherit_uid' and 'master' in dir(self):  # if already inited
            if self.master.uid != value and self.inherit_uid:  # disable inheritance is uid changed
                self.inherit_uid = False

    @property
    def inherit_uid(self):
        try:
            return self._inherit_uid
        except AttributeError:
            default = True
            self.inherit_uid = default
            return default

    @inherit_uid.setter
    def inherit_uid(self, value: bool):
        assert isinstance(value, bool)
        self._inherit_uid = value

        if self.uid != self.master.uid and value:
            self.uid = self.master.uid

    @property
    def path(self):
        return self.master.path

    @path.setter
    def path(self, value):
        self.master.path = value
        if self.inherit_uid:
            self.uid = self.master.uid

    @path.deleter
    def path(self):
        self.master.path = ''

    def insert_link(self):
        self.master.insert_link(self.name, self.link_data(self.uid, self.coll))

    def update_link(self):
        self.master.update_link(self.name, self.link_data(self.uid, self.coll))

    def delete_link(self):
        key = ".".join((self.name, "_id"))
        self.master.coll.delete_many({key: self.uid})

    def insert(self, data, link=True):
        super(CSCollection, self).insert(data)
        if link:
            self.insert_link()

    def update(self, data, link=True):
        super(CSCollection, self).update(data)
        if link:
            self.update_link()

    def replace(self, data, link=True):
        super(CSCollection, self).replace(data)
        if link:
            self.update_link()

    def delete(self, unlink=True):
        super(CSCollection, self).delete()
        if unlink:
            self.delete_link()

