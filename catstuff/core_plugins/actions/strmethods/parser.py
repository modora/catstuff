from catstuff.tools.argparser import CSArgParser
import argparse
from .output import print_wrapper

__version__ = 1.0


class Parser(CSArgParser):
    __version__ = __version__

    class AttrsAction(argparse.Action):
        # https://stackoverflow.com/questions/8526675/python-argparse-optional-append-argument-with-choices
        CHOICES = ['method', 'plugin', 'signature', 'doc']

        def __call__(self, parser, namespace, values, option_string=None):
            if values:
                for value in values:
                    if value not in self.CHOICES:
                        message = ("invalid choice: {0!r} (choose from {1})"
                                   .format(value, ', '.join([repr(action) for action in self.CHOICES])))
                        raise argparse.ArgumentError(self, message)
                setattr(namespace, self.dest, values)

    class SortOrderAction(argparse.Action):
        # https://stackoverflow.com/questions/8526675/python-argparse-optional-append-argument-with-choices
        CHOICES = ['ascending', 'descending', 'asc', 'desc']

        def __call__(self, parser, namespace, value, option_string=None):
            if value.lower() not in self.CHOICES:
                message = ("invalid choice: {0!r} (choose from {1})"
                           .format(value, ', '.join([repr(action) for action in self.CHOICES])))
                raise argparse.ArgumentError(self, message)
            setattr(namespace, self.dest, value)

    def __init__(self):
        super().__init__(description='Shows all the methods for the CSStr class')
        self.add_argument('-t', type=int, default=4, help='tab width (default=4)')
        self.add_argument('-a', '--all', help='-b -r', action='store_true')

        self.add_argument('-b', '--builtins', help='Also show python str methods', action='store_true')
        self.add_argument('-r', '--replaced', help='Also show replaced str methods', action='store_true')

        self.add_argument('--sort-by', choices=self.AttrsAction.CHOICES,
                          help='(default=first attr specified)', required=False, metavar='ATTR')
        self.add_argument('--sort-order', default='ascending', action=self.SortOrderAction, help='(default=ascending)')
                          #choices=['ascending', 'descending', 'asc', 'desc'])
        self.add_argument('attrs', nargs='*', action=self.AttrsAction, default=['method', 'plugin'], choices=self.AttrsAction.CHOICES)

        self.set_defaults(func=print_wrapper)
