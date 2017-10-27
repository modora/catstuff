## CSModule
### API
**class CSModule(*name, build, uid=None,
database=None, connection=None,
master_db=None, master_conn=None*)**

*name*: Name of the module
*build*: Build version of the module

### Usage
The `importCore` function serves as convenience function
for the `CSModule` object. This function parses the core
section of`.plugin` config file and returns
*name, build, module_path*

Consider this cut-down implementation of the fstat module
```python
import catstuff.toolbox.modules as mods
import os

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.importCore(os.path.join(__dir__, "fstat.plugin"))

class FStat(mods.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

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
        data = self.data()

        self.insert(data)
        return data

```

