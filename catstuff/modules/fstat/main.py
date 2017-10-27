import catstuff.tools.modules
import os
import logging
import pymongo

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = catstuff.tools.modules.importCore(os.path.join(__dir__, "fstat.plugin"))


class FStat(catstuff.tools.modules.CSCollection):
    indexes = ("device", "inode", "size", "mod_time")

    def __init__(self):
        super().__init__(__mod__, __build__)
        self.coll.create_indexes([
            pymongo.IndexModel([(index, pymongo.ASCENDING)], name=index) for index in self.indexes
        ])

    def __getattribute__(self, item):
        if item == 'data' and self.path == '':
            raise AttributeError('Path not set')
        else:
            return super().__getattribute__(item)

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
        self.set_path(path)
        result = self.data()

        self.insert(result)
        return result
