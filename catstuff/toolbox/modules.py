from yapsy.IPlugin import IPlugin
from configparser import ConfigParser
import catstuff.toolbox.db as db


class CSModule(IPlugin, db.Collection):
    def __init__(self, name, build, uid=None, database=None, connection=None,
                 master_db=None, master_conn=None):
        db.Collection.__init__(self, name, db=database, conn=connection, uid=uid)
        IPlugin.__init__(self)

        self.build = build

        self.path = ''
        self.master = db.Master(self.path, db=master_db, conn=master_conn)

    def main(self, *args, **kwargs):
        print("Executed the '{name}' module using the main method with arguments: {args} and keywords {kwargs}".format(
            name=self.name, args=args, kwargs=kwargs))

    def set_path(self, path, inherit_uid=True):
        self.path = path
        self.master.set_path(path)
        self.uid = self.master.uid if inherit_uid else self.uid

    def link(self, status='present'):
        self.master.link(self.name, self.build, mod_uid=self.uid, status=status, collection=self.coll)

    def unlink(self, unique=False):
        self.master.unlink(self.name, mod_uid=self.uid, unique=unique)

    def insert(self, data, link=True):
        db.Collection.insert(self, data)
        self.link() if link else None

    def replace(self, data, link=True):
        db.Collection.replace(self, data)
        self.link() if link else None

    def delete(self, unlink=True):
        db.Collection.delete(self)
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
