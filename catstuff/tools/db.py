import pymongo, bson
import logging
import uuid, datetime, time
from catstuff.tools.misc import is_path_exists_or_creatable

def generate_uid(method):
    if method == 'uuid':
        uid = uuid.uuid4().hex
    elif method == 'objectid':
        uid = bson.ObjectId()
    else:
        raise NotImplementedError
    return uid


def test_connection(connection=None):
    connection = pymongo.MongoClient() if connection is None else connection
    assert isinstance(connection, pymongo.MongoClient)
    try:
        connection.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        # should do logging here
        raise


def unpack_mongo_collection(collection: pymongo.collection.Collection):
    """ Returns the details necessary for establishing a connection to a collection"""
    coll = collection.name
    db = collection.database.name
    host, port = collection.database.client.address

    return (host, port, db, coll)


def unpack_mongo_database(database: pymongo.database.Database):
    """ Returns the details necessary for establishing a connection to a database"""
    db = database.name
    host, port = database.client.address

    return (host, port, db)


def unpack_mongo_connection(client: pymongo.MongoClient):
    """ Returns the details necessary for establishing a connection to a mongodb server"""
    return client.address


def unpack_mongo_details(pymongo_object):
    """ Convenience wrapper for unpacking mongodb objects"""
    return {
        pymongo.MongoClient: unpack_mongo_collection,
        pymongo.database.Database: unpack_mongo_database,
        pymongo.collection.Collection: unpack_mongo_collection,
    }[type(pymongo_object)](pymongo_object)


def link_data(uid, collection: pymongo.collection.Collection, src_coll=None) -> dict:
    """
    Formats all the necessary data to link a mongo document to another mongo document
    :param uid: "_id" of the target document
    :param collection: the mongodb collection that the target document resides in
    :type: pymongo.collection.Collection
    :param: src_coll: the mongodb collection that the source document resides in
    :type: (pymongo.collection.Collection, None)
    :return: minimum connection settings needed to connect to the target collection
    :rtype: dict

    :Note: The return data is the **minimum** required connection settings. This shows the differences in the
    connection settings between the current collection and the target collection. If the target document is in the
    same collection, then the link_data will be an empty dictionary
    """

    if src_coll is None:
        # some random database that should never be created -- this should get overridden anyways
        src_coll = pymongo.MongoClient()['catstuff']['__catstuff_db_error']
    assert isinstance(src_coll, pymongo.collection.Collection)

    attrs = ('host', 'port', 'database', 'collection')
    data = {'_id': uid}
    for i, (other, current) in enumerate(zip(unpack_mongo_details(collection),
                                             unpack_mongo_details(src_coll))):
        if other != current:
            attr = attrs[i]
            data.update({attr: other})
    return data


def eval_link(src_data: pymongo.collection.Collection, link_data: dict, *args, **kwargs) -> (None, dict):
    """evaluates the lined document -- mongodb args are allowed"""
    host, port, db, coll = unpack_mongo_details(src_data)  # defaults

    host = link_data.get('host') or host
    port = link_data.get('port') or port
    db = link_data.get('database') or db
    coll = link_data.get('collection') or coll

    coll = pymongo.MongoClient(host, port)[db][coll]

    return coll.find_one({"_id": link_data['_id']}, *args, **kwargs)


def property_getter(obj, name, default=None):
    try:
        return getattr(obj, name)
    except AttributeError:
        setattr(obj, name, default)
        return default


class CSCollection:
    ## DEFAULTS
    # Overriding a list of messy list of default, class attributes is safer than overriding a dictionary of defaults

    @property
    def _default_conn(self):
        return property_getter(self, '__default_conn', default=pymongo.MongoClient())

    @_default_conn.setter
    def _default_conn(self, value: pymongo.MongoClient):
        assert isinstance(value, pymongo.MongoClient)
        self.__default_conn = value

    @property
    def _default_db(self):
        return property_getter(self, '__default_db', default=pymongo.database.Database(self._default_conn, 'catstuff'))

    @_default_db.setter
    def _default_db(self, value: pymongo.database.Database):
        assert isinstance(value, pymongo.database.Database)
        self.__default_db = value

    ## ACTUAL CODE
    def __init__(self, collection_name, db=None, uid_generate_method='uuid', **kwargs):
        self.name = collection_name

        self._db = db
        self.coll = pymongo.collection.Collection(self.db, self.name, **kwargs)

        test_connection(self._conn)

        self.__uid_generate_method = uid_generate_method

    @property
    def db(self):
        try:
            return self._db
        except AttributeError:
            self.db = self._default_db

    @db.setter
    def db(self, value: pymongo.database.Database):
        assert isinstance(value, pymongo.database.Database)
        self._db = value
        self._conn = value.client

    @property
    def conn(self):
        return property_getter(self, '_conn', default=self._default_conn)

    @property
    def uid(self):
        return property_getter(self, '_uid', default=self.generate_uid())

    @uid.setter
    def uid(self, value):
        self._uid = value

    def generate_uid(self, check_unique=True, max_time=30):
        """
        Generates a uid
        :param check_unique: Checks if the generated uid exists in db
        :param max_time: Maximum time to generate uid in seconds
        :return:
        """
        start_time = time.time()
        while True:  # do-while
            uid = generate_uid(method=self.__uid_generate_method)

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
        data = {**data, **self.pre_data}  # append pre_data with actual data
        self.coll.update_one({"_id": self.uid}, {'$set': data}, upsert=True)

    def insert(self, data):
        self.__insert(data)

    def update(self, data):
        # alias for insert
        self.__insert(data)

    def __replace(self, data):
        data = {**data, **self.pre_data}  # append pre_data with actual data
        self.coll.replace_one({"_id": self.uid}, data, upsert=True)

    def replace(self, data):
        self.__replace(data)

    def __delete(self):
        self.coll.delete_one({"_id": self.uid})

    def delete(self):
        self.__delete()

    def link_data(self, uid, collection: pymongo.collection.Collection) -> dict:
        """
        Formats all the necessary data to link a mongo document to another mongo document
        :param uid: "_id" of the target document
        :param collection: the mongodb collection tht the target document resides in
        :type: pymongo.collection.Collection
        :return: minimum connection settings needed to connect to the target collection
        :rtype: dict

        :Note: The return data is the **minimum** required connection settings. This shows the differences in the
        connection settings between the current collection and the target collection. If the target document is in the
        same collection, then the link_data will be an empty dictionary
        """

        return link_data(uid, collection, src_coll=self.coll)

    def eval_link(self, link_data: dict, *args, **kwargs) -> (None, dict):
        """evaluates the lined document -- mongodb args are allowed"""
        return eval_link(self.coll, link_data, *args, **kwargs)

    def get(self, *args, default=None, **kwargs) -> dict:
        return self.coll.find_one({"_id": self.uid}, *args, **kwargs) or default

    def _print_defaults(self):
        """ CONVENIENCE FUNCTION FOR DEVS: Prints all class attributes that whose name starts with '_default_'"""
        string = '_default_'
        N = len(string)
        for attr in dir(self):
            if attr[:N] == string:
                print(attr, ":", getattr(self, attr))


class Master(CSCollection):
    """
    A random, unique-uid is generated when this class is initialized. This uid does not exist in database. Manually
    changing the uid to an existing id will also set the path
    """
    index_keys = {"status", "build", "last_updated"}
    special_names = {'_id', 'group', 'path'}

    def __init__(self, path='', db=None, uid_generate_method='uuid'):
        assert isinstance(path, (str, type(None)))

        super().__init__('master', db=db, uid_generate_method=uid_generate_method)

        self.path = path

        self.coll.create_indexes([
            pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index)
            for index in self.special_names
            if index != '_id'
        ])

    @property
    def path(self):
        if self._path in ('', None):
            raise AttributeError("Path not set")
        return self._path

    @path.setter
    def path(self, value):
        if value in (None, ''):
            self._path = ''
            return

        if not is_path_exists_or_creatable(value):
            raise OSError
        else:
            self._path = value

        existing_uid = (self.coll.find_one({'path': value}, {"_id": 1}) or {}).get('_id')

        if existing_uid is not None:
            self.uid = existing_uid

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

        # indexes = ['.'.join((mod_name, key)) for key in self.index_keys]
        # self.coll.create_indexes([
        #     pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in indexes
        # ])

    def update_link(self, mod_name, mod_data: dict):
        """ An alias for insert_link"""
        self.update(self.data(mod_name, mod_data))

    def delete_link(self, mod_name):
        self.coll.update_one({"_id": self.uid}, {'$unset': {mod_name: ""}})

    def get_raw(self, default=None) -> dict:
        # Returns the mongodb document
        return super().get(default=default)

    def get(self, default=None, eval_links=True, **kwargs) -> dict:
        # Returns the mongodb document and evaluates all the links
        master_doc = self.get_raw()
        if master_doc is None:
            return default
        if not eval_links:
            return master_doc or default
        d = {}
        for mod in master_doc.keys():
            if mod in self.special_names:
                d[mod] = master_doc[mod]
                continue
            d[mod] = self.eval_link(master_doc[mod])
        return d