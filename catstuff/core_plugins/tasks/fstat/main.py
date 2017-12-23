import os
import pymongo

import catstuff.core.dbs
import catstuff.tools.db
from catstuff import core

from .config import mod_name, build


class FStat(core.plugins.CSTask, catstuff.core.dbs.CSCollection):
    indexes = ("device", "inode", "size", "mod_time")

    def __init__(self):
        core.plugins.CSTask.__init__(self, mod_name, build)
        catstuff.core.dbs.CSCollection.__init__(self, mod_name)

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
