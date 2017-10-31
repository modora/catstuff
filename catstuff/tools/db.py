import pymongo, bson
import logging
import uuid, datetime
import collections


def connect(host='localhost', port=27017):
    try:
        conn = pymongo.MongoClient(host=host, port=port)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        logging.error("Could not connect to MongoDB: {}".format(e))


class Collection:
    def __init__(self, collection_name, db=None, uid=None, uid_generate_method='uuid'):
        self.name = collection_name

        # set_db
        if db is None:
            conn = connect()
            db = pymongo.database.Database(conn, 'catstuff')
        else:
            assert isinstance(db, pymongo.database.Database)
            conn = db._Database__client

        self.conn = conn
        self.db = db
        self.coll = pymongo.collection.Collection(self.db, self.name)

        # set uid
        self.uid = self.generate_uid(method=uid_generate_method) if uid is None else uid

    def _get_existing(self, qry, fields):
        assert isinstance(fields, collections.Iterable)
        if isinstance(fields, str):
            fields = (fields,)

        collation = {field: 1 for field in fields}
        result = self.coll.find_one(qry, collation) or {}  # return an empty dict if none
        return {**{field: None for field in fields}, **result}  # result a None value for nonexistent fields

    def set_db(self, db):
        if db is None:
            conn = connect()
            db = pymongo.database.Database(conn, 'catstuff')
        else:
            assert isinstance(db, pymongo.database.Database)
            conn = db._Database__client

        self.conn = conn
        self.db = db
        self.coll = pymongo.collection.Collection(self.db, self.name)

        result = (self.coll, self.db, self.conn)
        return result

    def set_uid(self, uid, uid_generate_method='uuid', check_unique=True):
        self.uid = self.generate_uid(method=uid_generate_method, check_unique=check_unique) if uid is None else uid
        return self.uid

    def replace_uid(self, new_uid=None, uid_generate_method='uuid'):
        # replaces the uid of the document in the collection
        # the _id field in the document is immutable so a copy-and-delete operation is necessary
        doc = self.get()
        new_uid = self.generate_uid(method=uid_generate_method, check_unique=True) if new_uid is None else new_uid
        self.coll.insert_one({**doc, **{"_id": new_uid}})
        self.delete()
        self.set_uid(new_uid)
        return self.uid

    def generate_uid(self, method, check_unique=True):
        while True:  # do-while
            if method == 'uuid':
                uid = uuid.uuid4().hex
            elif method == 'objectid':
                uid = bson.ObjectId()
            else:
                raise NotImplementedError
            if check_unique:
                # didn't want to use an 'AND' statement to avoid db operations
                if self.coll.find_one({"_id": uid}) is None:
                    break
            else:
                return uid
        return uid

    def pre_data(self):
        # constant data
        # This method is preferred since fields can be generated at runtime
        return {"_id": self.uid}

    def insert(self, data):
        pre_data = self.pre_data()
        data = {**data, **pre_data}  # append pre_data with actual data
        self.coll.update_one({"_id": self.uid}, {'$set': data}, upsert=True)

    def update(self, data):
        # alias for insert
        self.insert(data)

    def replace(self, data):
        pre_data = self.pre_data()
        data = {**data, **pre_data}  # append pre_data with actual data
        self.coll.replace_one({"_id": self.uid}, data, upsert=True)

    def delete(self):
        self.coll.delete_one({"_id": self.uid})

    def get(self, fields=None, default=None):
        if fields is None:
            result = self.coll.find_one({"_id": self.uid})
        else:
            assert isinstance(fields, collections.Iterable)
            fields = (fields,) if isinstance(fields, str) else fields
            collation = {field: 1 for field in fields}
            result = self.coll.find_one({"_id": self.uid}, collation)
        return result or default


class Master(Collection):
    index_keys = ("status", "build", "last_updated")

    def __init__(self, path='', uid=None, db=None, uid_generate_method='uuid'):
        assert isinstance(path, (str, type(None)))
        if path is None:
            path = ''

        super().__init__('master', db=db, uid=uid, uid_generate_method=uid_generate_method)

        self.path = path

        self.coll.create_index("path", name="path")

    def __getattribute__(self, item):
        if item == 'pre_data' and self.path == '':  # Do not insert data until path is set
            raise AttributeError("Path not set")
        else:
            return super().__getattribute__(item)

    def set_path(self, path):
        assert isinstance(path, (str, type(None)))
        if path is None:
            path = ''

        self.path = path

        existing_uid = self._get_existing({'path': self.path}, fields="_id")["_id"]

        if self.uid != existing_uid and existing_uid is not None:
            if existing_uid is not None:
                print('Specified uid changed from {old} to {new}'.format(old=self.uid, new=existing_uid))
            self.uid = existing_uid
        return self.path

    def set_uid(self, uid, uid_generate_method='uuid', check_unique=True):
        super().set_uid(uid, uid_generate_method=uid_generate_method, check_unique=check_unique)

        existing_path = self._get_existing({'_id': self.uid}, fields="path").get("path")

        if self.path != existing_path and existing_path is not None:
            if self.path not in ('', None):
                print('Specified path changed from {old} to {new}'.format(old=self.path, new=existing_path))
            self.path = existing_path
        return self.uid

    def pre_data(self):
        return {"_id": self.uid, "path": self.path}

    def data(self, mod_name, build, mod_uid=None, collection=None, status='present'):
        '''
        Returns the data in this collection
        :param mod_name: Module name
        :param build: Module build number
        :param mod_uid: Module UID (defaults to master uid)
        :param collection: Module collection object (used to parse db info)
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
        self.coll.create_indexes([
            pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in indexes
        ])
        self.insert(self.data(mod_name, build, mod_uid=mod_uid, collection=collection, status=status))

    def unlink(self, mod_name, mod_uid=None, unique=False):
        # unlinks any document with the uid -- if the link is known to be unique, set the unique option True
        mod_uid = self.uid if mod_uid is None else mod_uid
        if unique:
            self.coll.update_one({'.'.join((mod_name, "_id")): mod_uid}, {'$unset': {mod_name: ""}})
        else:
            self.coll.update_many({'.'.join((mod_name, "_id")): mod_uid}, {'$unset': {mod_name: ""}})
            # It seems mongodb automatically deletes an index if there are no elements in it
            # Therefore we don't need to use the api to delete the indices ourselves
            # for index in ['.'.join((move, key)) for key in self.index_keys]:
            #     self.coll.drop_index(index)  # custom named indexes must be dropped by name

    def get_raw(self, default=None):
        # Returns the mongodb document
        return super().get(default=default)

    def get(self, mods=None, default=None):
        # Returns the mongodb document and evaluates all the links
        doc = self.get_raw(default=None)
        if doc is None:
            return default
        mods = doc.keys() if mods is None else mods
        mods = (mods,) if isinstance(mods, str) else mods  # convert str to tuple
        assert isinstance(mods, collections.Iterable)
        d = {}
        for mod in mods:
            if mod in {'_id', 'path'}:
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