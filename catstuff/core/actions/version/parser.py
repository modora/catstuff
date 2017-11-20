from catstuff.tools.argparser import CSArgParser
from catstuff.core.actions.version import __version__


class Parser(CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.set_defaults(func=print_version)


def print_version(args):
    # All arguments are ignored right now
    print(__version__)
