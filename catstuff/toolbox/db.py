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
    def __init__(self, collection, db=None, conn=None, uid=None, uid_generate_method='uuid'):
        if db is not None:
            assert isinstance(db, pymongo.database.Database)
            conn = db._Database__client
        else:
            assert isinstance(conn, (type(None), pymongo.MongoClient))
            conn = connect(host='localhost', port=27017) if conn is None else conn
            db = pymongo.database.Database(conn, 'catstuff')
        self.conn = conn
        self.db = db

        self.name = collection
        self.coll = pymongo.collection.Collection(self.db, self.name)
        self.uid = self.generate_uid(method=uid_generate_method) if uid is None else uid

    @staticmethod
    def generate_uid(method):
        if method == 'uuid':
            return uuid.uuid4().hex
        elif method == 'objectid':
            return bson.ObjectId()
        else:
            raise NotImplementedError

    def pre_data(self):
        # constant data
        # This method is preferred since fields can be generated at runtime
        return {"_id": self.uid}

    def insert(self, data):
        pre_data = self.pre_data()
        data = {**data, **pre_data}  # append pre_data with actual data
        self.coll.update_one({"_id": self.uid}, {'$set': data}, upsert=True)

    def replace(self, data):
        pre_data = self.pre_data()
        data = {**data, **pre_data}  # append pre_data with actual data
        self.coll.replace_one({"_id": self.uid}, data, upsert=True)

    def delete(self):
        self.coll.delete_one({"_id": self.uid})

    def get(self, default=None):
        result = self.coll.find_one({"_id": self.uid})
        return result if default is None else result


class Master(Collection):
    def __init__(self, path='', uid=None, db=None, conn=None):
        super().__init__('master', db=db, conn=conn, uid=uid)

        self.path = ''
        self.set_path(path) if path != '' else None

        if uid is not None:
            existing_path = self.coll.find_one({'_id': uid},{"path": 1})
            self.path = existing_path["path"] if existing_path is not None else self.path

        self.coll.create_index("path")

    def __getattribute__(self, item):
        if item == 'pre_data' and self.path == '':
            raise AttributeError("Path not set")
        else:
            return super().__getattribute__(item)

    def set_path(self, path):
        self.path = path
        existing_uid = self.coll.find_one({'path': self.path}, {"_id": 1})
        self.uid = existing_uid["_id"] if existing_uid is not None else self.uid

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
        self.insert(self.data(mod_name, build, mod_uid=mod_uid, collection=collection, status=status))

    def unlink(self, mod_name, mod_uid=None, unique=False):
        # unlinks any document with the uid -- if the link is known to be unique, set the unique option True
        mod_uid = self.uid if mod_uid is None else mod_uid
        if unique:
            self.coll.update_one({'.'.join((mod_name, "_id")): mod_uid}, {'$unset': {mod_name: ""}})
        else:
            self.coll.update_many({'.'.join((mod_name, "_id")): mod_uid}, {'$unset': {mod_name: ""}})

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