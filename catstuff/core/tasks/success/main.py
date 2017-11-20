import catstuff.tools.plugins
from catstuff.core.tasks.success import mod_name, build


class Success(catstuff.tools.plugins.CSTask):
    def __init__(self):
        super().__init__(mod_name, build)

    def main(self, **kwargs):
        msg = "Success"
        print(msg)
        return msg


if __name__ == '__main__':
    Success().main()
