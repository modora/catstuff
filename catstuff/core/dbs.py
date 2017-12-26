import collections
import time

import pymongo


# These unused are left here for documentation purposes
# The actual imports happen within the function statements but
# I like to keep these here so I know there are cross-module dependencies


class _CSBaseCollection:
    """ High level API wrapper for the catstuff mongodb"""
    ## DEFAULTS
    # Overriding a list of messy list of default, class attributes is safer than overriding a dictionary of defaults

    @property
    def _default_conn(self):
        from catstuff.core import vars

        try:
            return self.__default_conn
        except AttributeError:
            config = vars.CSVarPool.get('config', app='catstuff')
            settings = config.get(['plugins', 'db', 'mongodb', 'client'], default={})
            host = settings.pop('host', 'localhost')
            self.__default_conn = pymongo.MongoClient(host, **settings)
            return self._default_conn

    @property
    def _default_db(self):
        from catstuff.core import vars

        try:
            return self.__default_db
        except AttributeError:
            config = vars.CSVarPool.get('config', app='catstuff')
            settings = config.get(['plugins', 'db', 'mongodb', 'db'], default={})
            name = settings.pop('name', 'catstuff')
            self.__default_db = pymongo.database.Database(self._default_conn, name, **settings)
            return self._default_db

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, value):
        if value is None:
            self._db = self._default_db
        else:
            if isinstance(value, pymongo.database.Database):
                self._db = value
            else:
                raise TypeError('db is not a pymongo database instance')

    @property
    def coll(self):
        return self._coll

    @property
    def _uid_generate_method(self):
        return self.__uid_generate_method

    @_uid_generate_method.setter
    def _uid_generate_method(self, value):
        from catstuff.tools import db
        db.generate_uid(method=value)
        self.__uid_generate_method = value

    @property
    def uid(self):
        try:
            return self._uid
        except AttributeError:
            self._uid = self.generate_uid()
            return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    ## ACTUAL CODE
    def __init__(self, collection_name, db=None, uid_generate_method='uuid', **kwargs):
        self.name = collection_name

        self.db = db
        self._coll = pymongo.collection.Collection(self.db, self.name, **kwargs)

        self._uid_generate_method = uid_generate_method

    def generate_uid(self, check_unique=True, max_time=30):
        """
        Generates a uid
        :param check_unique: Checks if the generated uid exists in db
        :param max_time: Maximum time to generate uid in seconds
        :return:
        """
        from catstuff.tools import db

        start_time = time.time()
        while True:  # do-while
            uid = db.generate_uid(method=self.__uid_generate_method)

            if check_unique:
                # didn't want to use an 'AND' statement to avoid db operations
                if self.coll.find_one({"_id": uid}) is None:
                    break
            elif time.time() - start_time > max_time:
                raise RuntimeError('uuid took too long to generate')
            else:
                break
        return uid

    @property
    def pre_data(self):
        return {"_id": self.uid}

    def __insert(self, data):
        """ Base insert method"""
        data = {**data, **self.pre_data}  # append pre_data with actual data
        self.coll.update_one({"_id": self.uid}, {'$set': data}, upsert=True)

    def insert(self, data):
        self.__insert(data)

    def update(self, data):
        """ Alias for insert"""
        self.__insert(data)

    def __replace(self, data):
        """ Base replace method"""
        data = {**data, **self.pre_data}  # append pre_data with actual data
        self.coll.replace_one({"_id": self.uid}, data, upsert=True)

    def replace(self, data):
        self.__replace(data)

    def __delete(self):
        """ Base delete method"""
        self.coll.delete_one({"_id": self.uid})

    def delete(self):
        self.__delete()

    def link_data(self, uid, collection: pymongo.collection.Collection) -> dict:
        """
        Formats all the necessary data to link a mongo document to another mongo document
        :param uid: "_id" of the target document
        :param collection: the mongodb collection tht the target document resides in
        :type: pymongo.collection._CSBaseCollection
        :return: minimum connection settings needed to connect to the target collection
        :rtype: dict

        :Note: The return data is the **minimum** required connection settings. This shows the differences in the
        connection settings between the current collection and the target collection. If the target document is in the
        same collection, then the link_data will be an empty dictionary
        """
        from catstuff.tools import db
        return db.link_data(uid, collection, src_coll=self.coll)

    def eval_link(self, link_data: dict, *args, **kwargs) -> (None, dict):
        """evaluates the lined document -- mongodb args are allowed"""
        from catstuff.tools import db
        return db.eval_link(self.coll, link_data, *args, **kwargs)

    def get(self, *args, default=None, **kwargs) -> dict:
        return self.coll.find_one({"_id": self.uid}, *args, **kwargs) or default


class CSMaster(_CSBaseCollection):
    """
    A random, unique-uid is generated when this class is initialized. This uid does not exist in database. Manually
    changing the uid to an existing id will also set the path
    """
    index_keys = {"status", "build", "last_updated"}
    special_names = {'_id', 'group', 'path'}

    def __init__(self, path='', uid_generate_method='uuid'):
        assert isinstance(path, (str, type(None)))

        super().__init__('master', db=None, uid_generate_method=uid_generate_method)

        self.path = path

        # self.coll.create_indexes([
        #     pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index)
        #     for index in self.special_names
        #     if index != '_id'
        # ])

    @property
    def path(self):
        if self._path in {'', None}:
            raise AttributeError("Path not set")
        return self._path

    @path.setter
    def path(self, value):
        from catstuff.tools import path

        if value in {None, ''}:
            self._path = ''
            return

        if not path.is_path_exists_or_creatable(value):
            raise OSError("Invalid path")
        else:
            self._path = value

        existing_uid = (self.coll.find_one({'path': value}, {"_id": 1}) or {}).get('_id')

        if existing_uid is not None:
            self._uid = existing_uid

    @path.deleter
    def path(self):
        self._path = ''

    @property
    def pre_data(self):
        return {"_id": self.uid, "path": self.path}

    @staticmethod
    def data(mod_name, data_: dict):
        '''
        Returns the formatted data in this collection
        '''

        return {mod_name: data_}

    def insert_link(self, mod_name, mod_data: dict):
        self.insert(self.data(mod_name, mod_data))

        # TODO: Implement indices
        # indexes = ['.'.join((mod_name, key)) for key in self.index_keys]
        # self.coll.create_indexes([
        #     pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in indexes
        # ])

    def update_link(self, mod_name, mod_data: dict):
        """ An alias for insert_link"""
        self.update(self.data(mod_name, mod_data))

    def delete_link(self, mod_name):
        self.coll.update_one({"_id": self.uid}, {'$unset': {mod_name: ""}})

    def get_raw(self, *args, default=None, **kwargs) -> dict:
        # Returns the mongodb document
        return super().get(*args, default=default, **kwargs)

    def get(self, *args, default=None, eval_links=True, **kwargs) -> dict:
        # Returns the mongodb document and evaluates all the links
        master_doc = self.get_raw(*args, default=default, **kwargs)
        if master_doc is None:
            return default
        if not eval_links:
            return master_doc or default
        d = collections.defaultdict(dict)
        for mod in master_doc:
            if mod in self.special_names:
                d[mod] = master_doc[mod]
            else:
                d[mod] = self.eval_link(master_doc[mod])
        return dict(d)


class CSCollection(_CSBaseCollection):
    """ Create a catstuff task with built-in mongodb api"""
    def __init__(self, name, *, database=None, master_db=None, inherit_uid=True, link=True, **kwargs):
        super().__init__(name, database, **kwargs)

        self._inherit_uid = inherit_uid
        self._link = link
        self.master = CSMaster(db=(master_db or self._default_db))
        self.path = None

    @property
    def uid(self):
        if self.inherit_uid:
            return self.master.uid
        else:
            return super().uid

    @property
    def inherit_uid(self):
        return self._inherit_uid

    @property
    def path(self):
        return self.master.path

    @path.setter
    def path(self, value):
        self.master.path = value

    @path.deleter
    def path(self):
        self.master.path = ''

    def insert(self, data, link=True):
        super().insert(data)
        if link:
            self.master.insert_link(self.name, self.link_data(self.uid, self.coll))

    def update(self, data, link=True):
        super().update(data)
        if link:
            self.master.update_link(self.name, self.link_data(self.uid, self.coll))

    def replace(self, data, link=True):
        super().replace(data)
        if link:
            self.master.update_link(self.name, self.link_data(self.uid, self.coll))

    def delete(self, unlink=True):
        super().delete()
        if unlink:
            key = ".".join((self.name, "_id"))
            self.master.coll.delete_many({key: self.uid})