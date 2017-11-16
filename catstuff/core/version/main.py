import catstuff.tools.plugins, catstuff.tools.parser
import os

_dir = os.path.dirname(os.path.realpath(__file__))
_plugin_file = os.path.join(_dir, "version.plugin")
__version__ = catstuff.tools.plugins.import_documentation(_plugin_file).get('Version')

name, _, _ = catstuff.tools.plugins.import_core(_plugin_file)

# version = 'CatStuff: {catstuff}\n' \
#           'Parser: {parser}'.format(
#     catstuff=catstuff.__version__, parser=parser.__version__)

version = catstuff.__version__


class _VersionArgParse(catstuff.tools.parser.CSArgParser):
    """ Argument parser for the version plugin"""
    pass


class Version(catstuff.tools.plugins.CSAction):
    def __init__(self):
        super().__init__(name)


    @staticmethod
    def main(*args):
        _parser.parse_args(*args)
        print(version)


_parser = _VersionArgParse()
_parser.add_argument('--version', action='version', version=__version__)


if __name__ == '__main__':
    Version.main()