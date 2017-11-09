import catstuff.tools.modules
import os
import logging
import pymongo

_dir = os.path.dirname(__file__)
_plugin_file = os.path.join(_dir, "fstat.plugin")
__version__ = catstuff.tools.modules.import_documentation(_plugin_file).get('Version')

_mod, _build, _ = catstuff.tools.modules.import_core(_plugin_file)


class FStat(catstuff.tools.modules.CSCollection):
    indexes = ("device", "inode", "size", "mod_time")

    def __init__(self):
        super().__init__(_mod, _build)
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
