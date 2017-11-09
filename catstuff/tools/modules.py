from yapsy.IPlugin import IPlugin
import configparser
import catstuff.tools.db
import catstuff.tools.config
import pymongo


class CSModule(IPlugin):
    def __init__(self, name, build):
        super().__init__()
        self.name = name
        self.build = build

    def main(self, **kwargs):
        print("Executed main method of '{name}' module of class '{cls}' with arguments: {kwargs}".format(
            name=self.name, kwargs=kwargs, cls=self.__class__.__name__))


class CSCollection(catstuff.tools.db.Collection, CSModule):
    def __init__(self, name, build, path='', database=None, master_db=None, inherit_uid=True):
        catstuff.tools.db.Collection.__init__(self, name, db=database)
        CSModule.__init__(self, name, build)

        self.master = catstuff.tools.db.Master(db=master_db)
        self.inherit_uid = inherit_uid
        self.path = path

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        catstuff.tools.db.Collection.uid.fset(self, value)  # this is correct -- warnings are wrong

        if 'inherit_uid' and 'master' in dir(self):  # if already inited
            if self.master.uid != value and self.inherit_uid:  # disable inheritance is uid changed
                self.inherit_uid = False

    @property
    def inherit_uid(self):
        return self._inherit_uid

    @inherit_uid.setter
    def inherit_uid(self, value: bool):
        assert isinstance(value, bool)
        self._inherit_uid = value

        if self.uid != self.master.uid and value:
            self.uid = self.master.uid

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self.master.path = value
        if self.inherit_uid:
            self.uid = self.master.uid

    @path.deleter
    def path(self):
        self._path = ''
        self.master.path = ''

    def link(self, status='present'):
        self.master.link(self.name, self.build, mod_uid=self.uid, status=status, collection=self.coll)

    def unlink(self):
        self.master.unlink(self.name, mod_uid=self.uid)

    def insert(self, data, link=True):
        try:
            catstuff.tools.db.Collection.insert(self, data)
            status = 'present'
        except pymongo.errors.PyMongoError as e:
            status = 'failed'
        if link:
            self.link(status=status)

    def replace(self, data, link=True):
        try:
            catstuff.tools.db.Collection.replace(self, data)
            status = 'present'
        except pymongo.errors.PyMongoError as e:
            status = 'failed'
        if link:
            self.link(status=status)

    def delete(self, unlink=True):
        catstuff.tools.db.Collection.delete(self)
        if unlink:
            self.unlink()


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


def __get_opt(config: dict, option: str):
    # returns a key of a dict (first letter, case insensitive)
    return config.get(option) or config.get(option.lower()) or config.get(option.capitalize())


def import_core(path):
    options = ['name', 'build', 'module']

    config = read_config(path)
    config = __get_opt(config, option='Core') or {}

    return tuple([__get_opt(config, opt) for opt in options])


def import_documentation(path):
    config = read_config(path)
    return __get_opt(config, 'Documentation')
