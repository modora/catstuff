import catstuff.toolbox.modules as mods
# from catstuff.toolbox.modules import CSModule  # DO NOT IMPORT THIS WAY -- PLUGIN WILL ERROR AT THE INIT
import os
import logging

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.importCore(os.path.join(__dir__, "fstat.plugin"))


class FStat(mods.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

    # def __getattribute__(self, item):
    #     if item == 'data' and self.path == '':
    #         raise AttributeError('Path not set')
    #     else:
    #         super().__getattribute__(item)

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

    def main(self, *args, **kwargs):
        self.set_path(kwargs['path'])
        result = self.data()

        self.insert(result)
        return result