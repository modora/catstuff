from catstuff.core_plugins.tasks.success import mod_name, build
from catstuff.core import plugins


class Success(plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, **kwargs):
        msg = "Success"
        print(msg)
        return msg


if __name__ == '__main__':
    Success().main()
