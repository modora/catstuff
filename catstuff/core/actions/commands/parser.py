from catstuff.tools.argparser import CSArgParser
from catstuff.core.actions.commands import __version__
from catstuff.core.actions.commands.formatter import print_wrapper


class Parser(CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('args', nargs='*', default=['Name', 'Version', 'Description'])
        self.add_argument('-t', default=4)
        self.set_defaults(func=print_wrapper)