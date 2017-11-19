from catstuff.tools.argparser import CSArgParser
from catstuff.core.actions.commands import __version__

class Parser(CSArgParser):
    def __init__(self):
        super().__init__()
        self.add_argument('--version', action='version', version=__version__)
        self.add_argument('args', nargs='*', default=['Name', 'Version', 'Description'])

parser = Parser()