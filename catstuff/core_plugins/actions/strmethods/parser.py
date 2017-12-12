from catstuff.tools.argparser import CSArgParser
from .output import print_wrapper

__version__ = 1.0


class Parser(CSArgParser):
    __version__ = __version__

    def __init__(self):
        super().__init__(description='Shows all the methods for the CSStr class')
        self.add_argument('-a', '--all', help='-b -r', action='store_true')

        self.add_argument('-b', '--builtins', help='Also show python str methods', action='store_true')
        self.add_argument('-r', '--replaced', help='Also show replaced str methods', action='store_true')

        self.add_argument('--sort-by', default='method', choices=['method', 'plugin'], help='(default=method)')
        self.add_argument('--sort-order', default='ascending', help='(default=ascending)',
                          choices=['ascending', 'descending', 'asc', 'desc'])
        self.set_defaults(func=print_wrapper)
