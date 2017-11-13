import pymongo, bson
import logging
import uuid, datetime, time
import collections
import socket


def generate_uid(method):
    if method == 'uuid':
        uid = uuid.uuid4().hex
    elif method == 'objectid':
        uid = bson.ObjectId()
    else:
        raise NotImplementedError
    return uid


def connect(*args, **kwargs):
    try:
        conn = pymongo.MongoClient(*args, **kwargs)
        conn.server_info()
        return conn
    except pymongo.errors.ServerSelectionTimeoutError as e:
        # should do logging here
        raise


class CSCollection:
    def __init__(self, collection_name, db=None, uid_generate_method='uuid'):
        self.name = collection_name

        self.db = db
        self.coll = pymongo.collection.Collection(self.db, self.name)

        self._uid_generate_method = uid_generate_method
        self._uid = self.generate_uid()

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, value: pymongo.database.Database):
        self._set_db(value)

    def _set_db(self, db, *args, **kwargs):
        """

        :param db:
        :param args: connect() arguments
        :param kwargs: connect() keyword args
        :return:
        """
        if db is None:
            conn = connect(*args, **kwargs)
            self._db = pymongo.database.Database(conn, 'catstuff')
        else:
            assert isinstance(db, pymongo.database.Database)
            self._db = db
        self._conn = self.db.client

    @property
    def conn(self):
        return self._conn

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value if value is not None else self.generate_uid()

    def generate_uid(self, check_unique=True, max_time=30):
        """

        :param check_unique:
        :param max_time: Maximum time to generate uid in seconds
        :return:
        """
        start_time = time.time()
        while True:  # do-while
            uid = generate_uid(method=self._uid_generate_method)

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

    @staticmethod
    def _get_coll_details(collection):
        coll = collection.name
        db = collection.database.name
        host, port = collection.database.client.address

        return (host, port, db, coll)

    def link_data(self, uid, collection: pymongo.collection.Collection) -> dict:
        """formats data to link a document to another document"""

        attrs = ('host', 'port', 'database', 'collection')
        data = {'_id': uid}
        for i, (other, current) in enumerate(zip(self._get_coll_details(collection),
                                               self._get_coll_details(self.coll))):
            if other != current:
                attr = attrs[i]
                data.update({attr: other})
        return data

    def eval_link(self, link_data: dict, *args, **kwargs) -> (None, dict):
        """evaluates the lined document -- mongodb args are allowed"""
        # defaults
        host, port, db, coll = self._get_coll_details(self.coll)

        host = link_data.get('host') or host
        port = link_data.get('port') or port
        db = link_data.get('database') or db
        coll = link_data.get('collection') or coll

        conn = pymongo.MongoClient(host, port)
        db = pymongo.database.Database(conn, name=db)
        coll = pymongo.collection.Collection(db, name=coll)

        return coll.find_one({"_id": link_data['_id']}, *args, **kwargs)

    def get(self, *args, default=None, **kwargs) -> dict:
        return self.coll.find_one({"_id": self.uid}, *args, **kwargs) or default


class Master(CSCollection):
    """
    A random, unique-uid is generated when this class is initialized. This uid does not exist in database. Manually
    changing the uid to an existing id will also set the path
    """
    index_keys = {"status", "build", "last_updated"}
    special_names = {'_id', 'group', 'path'}

    def __init__(self, path='', db=None, uid_generate_method='uuid', group='ungrouped'):
        assert isinstance(path, (str, type(None)))

        super().__init__('master', db=db, uid_generate_method=uid_generate_method)

        self.path = path
        self.group = group

        self.coll.create_index("path", name="path")

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
        self._path = value

        '''
        NotImplementedError(is_valid_path not defined)
        if not is_valid_path(value):
            raise OSError
        else:
            self._path = value
        '''
        existing_uid = (self.coll.find_one({'path': value}, {"_id": 1}) or {}).get('_id')

        if existing_uid is None:
            self.uid = self.generate_uid()
            return
        elif 'uid' not in dir(self):  # if uid not inited
            self.uid = existing_uid
        elif self.uid != existing_uid:
            self.uid = existing_uid
        # else, self.uid already equals existing_uid

    @path.deleter
    def path(self):
        self._path = ''

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value: str):
        assert isinstance(value, str)
        self._group = value

    @group.deleter
    def group(self):
        self._group = 'ungrouped'

    @property
    def pre_data(self):
        return {"_id": self.uid, "path": self.path, "group": self.group}

    def data(self, mod_name, build, mod_uid=None, collection=None, status='present'):
        '''
        Returns the data in this collection
        :param mod_name: Module name
        :param build: Module build number
        :param mod_uid: Module UID (defaults to master uid)
        :param collection: Module collection object (used to parse db info)
        :param status:
        :return:
        '''
        assert isinstance(collection, (type(None),pymongo.collection.Collection))
        collection = self.coll if collection is None else collection
        mod_uid = self.uid if mod_uid is None else mod_uid

        last_updated = datetime.datetime.now()

        data = {
            mod_name: {
                'status': status,
                'build': build,  # used for queries
                'last_updated': last_updated.timestamp(),  # used for queries
                **self.link_data(mod_uid, collection)
            }
        }
        return data

    def link(self, mod_name, build, status='present', mod_uid=None, collection=None):
        # links the document in the master database to a document in another collection

        indexes = ['.'.join((mod_name, key)) for key in self.index_keys]
        try:
            self.coll.create_indexes([
                pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in indexes
            ])
            self.insert(self.data(mod_name, build, mod_uid=mod_uid, collection=collection, status=status))
        except pymongo.errors.PyMongoError as e:
            print("Error creating master link: {}".format(e))
            raise pymongo.errors.PyMongoError(e)

    def unlink(self, mod_name, mod_uid=None):
        # unlinks any document with the uid
        mod_uid = self.uid if mod_uid is None else mod_uid
        try:
            self.coll.update_many({'.'.join((mod_name, "_id")): mod_uid}, {'$unset': {mod_name: ""}})
            # It seems mongodb automatically deletes an index if there are no elements in it
            # Therefore we don't need to use the api to delete the indices ourselves
            # for index in ['.'.join((move, key)) for key in self.index_keys]:
            #     self.coll.drop_index(index)  # custom named indexes must be dropped by name
        except pymongo.errors.PyMongoError as e:
            print("Error unlinking master link: {}".format(e))
            raise pymongo.errors.PyMongoError(e)

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
