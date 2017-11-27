from catstuff.tools import plugins
import os
import pymongo
# using from . import results in a cyclic import for some reason
# using pycycle shows no errors
from catstuff.core.tasks.fstat import mod_name, build


class FStat(plugins.CSCollection):
    indexes = ("device", "inode", "size", "mod_time")

    def __init__(self):
        super().__init__(mod_name, build)

        self.coll.create_indexes([
            pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in self.indexes
        ])

    def data(self):
        fd = os.open(self.path, os.O_RDONLY)
        result = os.fstat(fd)
        os.close(fd)

        return {
            'device': result.st_dev,
            'inode': result.st_ino,
            'size': result.st_size,  # in bytes
            'mod_time': result.st_mtime
        }

    def main(self, path, **kwargs):
        self.path = path
        result = self.data()

        self.insert(result)
        return result