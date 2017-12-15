from catstuff.core import plugins
from catstuff.core_plugins.tasks.checksum.config import mod_name, build


class Template(plugins.CSTask):
    def __init__(self, **kwargs):
        super().__init__(mod_name, build)  # everything above here is required

    def main(self):  # modify anything below here
        print('This is a sample plugin')
        return 'sample'
