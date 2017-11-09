import pymongo, bson
import logging
import uuid, datetime, time
import collections


def generate_uid(method):
    if method == 'uuid':
        uid = uuid.uuid4().hex
    elif method == 'objectid':
        uid = bson.ObjectId()
    else:
        raise NotImplementedError
    return uid


def connect(host='localhost', port=27017):
    try:
        conn = pymongo.MongoClient(host=host, port=port)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        logging.error("Could not connect to MongoDB: {}".format(e))


class Collection:
    def __init__(self, collection_name, db=None, uid_generate_method='uuid'):
        self.name = collection_name

        self.db = db
        self.coll = pymongo.collection.Collection(self.db, self.name)

        self._uid_generate_method = uid_generate_method
        self.uid = self.generate_uid()

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, value):
        if value is None:
            self._conn = connect()
            self._db = pymongo.database.Database(self._conn, 'catstuff')
        else:
            assert isinstance(value , pymongo.database.Database)
            self._conn = value._Database__client

    @property
    def conn(self):
        return self._conn

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        # replaces the id -- if document already exists, change the uid as well
        if value is None:
            new_uid = self.generate_uid()
        else:
            new_uid = value

        if '_uid' not in dir(self):  # if uid has not been initialized
            self._uid = new_uid
            return
        elif self._uid != value:
            self._replace_uid(new_uid)
            self._uid = new_uid

    def _replace_uid(self, new_uid):
        """ Replaces current document with new_uid"""

        doc = self.coll.find_one({"_id": self.uid})  # current uid
        # nothing to do if no document exists!!
        if doc is not None:
            # the _id field in the document is immutable so a copy-and-delete operation is necessary
            self.coll.insert_one({**doc, **{"_id": new_uid}})
            self.coll.delete_one({"_id": self.uid})
            print("doc uid changed from {old} to {new}".format(old=self.uid, new=new_uid))

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

    def _get_existing(self, qry, fields, append_missing=True):
        """ Returns the value(s) of the fields given in the document """
        """ Append_missing assigns mssing fields to the result """
        assert isinstance(fields, collections.Iterable)
        if isinstance(fields, str):
            fields = (fields,)

        collation = {field: 1 for field in fields}
        result = self.coll.find_one(qry, collation) or {}  # return an empty dict if none
        if append_missing:
            return {**{field: None for field in fields}, **result}  # result a None value for nonexistent fields
        else:
            return result

    def get(self, fields=None, default=None):
        if fields is None:
            result = self.coll.find_one({"_id": self.uid})
        else:
            result = self._get_existing({"_id": self.uid}, fields=fields, append_missing=False)
        return result or default


class Master(Collection):
    """
    A random, unique-uid is generated when this class is initialized. This uid does not exist in database. Manually
    changing the uid to an existing id will also set the path
    """
    index_keys = {"status", "build", "last_updated"}
    special_names = {'_id', 'group', 'path'}

    def __init__(self, path='', db=None, uid_generate_method='uuid', group='ungrouped'):
        assert isinstance(path, (str, type(None)))
        if path is None:
            path = ''

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
            self.uid = self.generate_uid()
            return
        self._path = value

        '''
        NotImplementedError(is_valid_path not defined)
        if not is_valid_path(value):
            raise OSError
        else:
            self._path = value
        '''
        existing_uid = self._get_existing({'path': value}, fields='_id')['_id']

        if existing_uid is None:
            self.uid = self.generate_uid()
            return
        elif 'uid' not in dir(self):
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
        coll_name = collection.name
        db_name = collection.database.name
        connection = collection.database._Database__client.address  # tuple of (hostname, port)

        data = {
            mod_name: {
                "_id": mod_uid,
                'status': status,
                'database': db_name,
                'connection': connection,
                'collection': coll_name,
                'build': build,  # used for queries
                'last_updated': last_updated.timestamp()  # used for queries
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

    def get_raw(self, default=None):
        # Returns the mongodb document
        return super().get(default=default)

    def get(self, mods=None, default=None):
        # Returns the mongodb document and evaluates all the links
        doc = self.get_raw(default=None)
        if doc is None:
            return default
        mods = doc.keys() if mods is None else mods
        mods = {mods} if isinstance(mods, str) else mods  # convert str to tuple
        assert isinstance(mods, collections.Iterable)
        d = {}
        for mod in mods:
            if mod in self.special_names:
                d[mod] = doc[mod]
                continue
            if mod not in doc:
                d[mod] = default
                continue
            id = doc[mod]['_id']
            host, port = doc[mod]['connection']
            db_name = doc[mod]['database']
            coll_name = doc[mod]['collection']

            conn = pymongo.MongoClient(host=host, port=port)
            db = pymongo.database.Database(conn, db_name)
            coll = pymongo.collection.Collection(db, coll_name)

            d[mod] = coll.find_one({"_id": id})
        return d