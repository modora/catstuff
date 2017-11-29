from .config import __version__
from .formatter import print_wrapper
from catstuff.tools.argparser import CSArgParser


class Parser(CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('args', nargs='*', default=['Name', 'Version', 'Description'])
        self.add_argument('-t', default=4)
        self.set_defaults(func=print_wrapper)
