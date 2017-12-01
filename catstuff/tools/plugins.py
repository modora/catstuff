from ._core import CSTask, CSAction, StrMethod
from . import _core
from .db import property_getter


class CSCollection(_core.CSMongoCollection, CSTask):
    """ Create a catstuff task with built-in mongodb api"""
    def __init__(self, name, build, database=None, master_db=None):
        _core.CSMongoCollection.__init__(self, name, db=database)
        CSTask.__init__(self, name, build)

        self.master = _core.CSMaster(db=(master_db or self._default_db))
        self.path = None

    @property
    def uid(self):
        return property_getter(self, '_uid', default=self.generate_uid())

    @uid.setter
    def uid(self, value):
        _core.CSMongoCollection.uid.fset(self, value)  # this is correct -- warnings are wrong

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

