from yapsy.IPlugin import IPlugin
import configparser
import catstuff.tools.db
import collections


class CSModule(IPlugin):
    def __init__(self, name, build):
        super().__init__()
        self.name = name
        self.build = build

    def main(self, **kwargs):
        print("Executed main method of '{name}' module of class '{cls}' with arguments: {kwargs}".format(
            name=self.name, kwargs=kwargs, cls=self.__class__.__name__))


class CSCollection(catstuff.tools.db.Collection, CSModule):
    def __init__(self, name, build, uid=None, path='', database=None, master_db=None):
        catstuff.tools.db.Collection.__init__(self, name, db=database, uid=uid)
        CSModule.__init__(self, name, build)

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


def read_config(path):
    """
    Reads an ini config file and returns it as a dict
    :param path:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(path)

    d = {}
    for section in config.sections():
        d[section] = {}
        for option in config.options(section):
            d[section][option] = config.get(section, option)
    return d


def _get_opt(config: dict, option: str):
    # returns a dict key (first letter, case insensitive)
    return config.get(option) or config.get(option.lower()) or config.get(option.capitalize())


def import_core(path):
    options = ['build', 'name', 'module']

    config = read_config(path)
    config = _get_opt(config, option='Core') or {}

    Core = collections.namedtuple('Core', options)
    return Core(
        build=_get_opt(config, 'build'),
        name=_get_opt(config, 'name'),
        module=_get_opt(config, 'module')
    )


def import_documentation(path):
    config = read_config(path)
    return _get_opt(config, 'Documentation')
