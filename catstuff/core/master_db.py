import pymongo
from catstuff import tools


class CSMaster(tools.db.Collection):
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

        if not tools.misc.is_path_exists_or_creatable(value):
            raise OSError("Invalid path")
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