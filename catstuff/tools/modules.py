from yapsy.IPlugin import IPlugin
from configparser import ConfigParser
import catstuff.tools.db


class CSObject(IPlugin):
    def __init__(self, name, build):
        super().__init__()
        self.name = name
        self.build = build

    def main(self, **kwargs):
        print("Executed main method of '{name}' module of class '{cls}' with arguments: {kwargs}".format(
            name=self.name, kwargs=kwargs, cls=self.__class__.__name__))


class CSCollection(catstuff.tools.db.Collection, CSObject):
    def __init__(self, name, build, uid=None, path='', database=None, master_db=None):
        catstuff.tools.db.Collection.__init__(self, name, db=database, uid=uid)
        CSObject.__init__(self, name, build)

        self.master = catstuff.tools.db.Master(db=master_db, uid=self.uid)

        self.path = ''
        self.set_path(path)

    def set_path(self, path, inherit_uid=True):
        self.path = path
        self.master.set_path(path)
        self.uid = self.master.uid if inherit_uid else self.uid

    def link(self, status='present'):
        self.master.link(self.name, self.build, mod_uid=self.uid, status=status, collection=self.coll)

    def unlink(self, unique=False):
        self.master.unlink(self.name, mod_uid=self.uid, unique=unique)

    def replace_uid(self, new_uid=None, uid_generate_method='uuid', unique=False):
        old_uid = self.uid

        doc = self.get()
        new_uid = self.generate_uid(method=uid_generate_method, check_unique=True) if new_uid is None else new_uid
        self.coll.insert_one({**doc, **{"_id": new_uid}})
        self.delete(unlink=False)
        self.set_uid(new_uid)

        field = '.'.join((self.name, "_id"))
        if unique:
            self.master.coll.update_one({field: old_uid}, {'$set': {field: self.uid}})
        else:
            self.master.coll.update_many({field: old_uid}, {'$set': {field: self.uid}})

    def insert(self, data, link=True):
        catstuff.tools.db.Collection.insert(self, data)
        self.link() if link else None

    def replace(self, data, link=True):
        catstuff.tools.db.Collection.replace(self, data)
        self.link() if link else None

    def delete(self, unlink=True):
        catstuff.tools.db.Collection.delete(self)
        self.unlink() if unlink else None


def importCore(path):
    config = ConfigParser()
    config.read(path)

    # Case insensitive options
    name = config.get('Core', 'Name') or config.get('Core', 'name')
    build = config.get('Core', 'Build') or config.get('Core', 'build')
    module = config.get('Core', 'Module') or config.get('Core', 'module')

    if any([key is None for key in (name, build, module)]):
        raise KeyError("Missing core key in {}".format(path))

    return name, build, module


def test():
    obj = CSObject('test', 1)
    obj.main()

if __name__ == '__main__':
    test()