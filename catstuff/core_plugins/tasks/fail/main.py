from catstuff.tools import plugins
from catstuff.core_plugins.tasks.fail.config import mod_name, build


class Fail(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, *args, **kwargs):
        raise NotImplementedError("Fail task has successfully executed!!")


if __name__ == '__main__':
    Fail().main()
