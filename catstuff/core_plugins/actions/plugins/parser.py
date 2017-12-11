from .version import print_wrapper
from .list import print_wrapper as list_print_wrapper
from catstuff.tools.argparser import CSArgParser


class Parser:  # Errors occur in adding the subparser when using class inheritance
    # Main parser
    __version__ = '1.0.2'

    @staticmethod
    def make(parser=CSArgParser()):  # constructs the parser
        parser.add_argument('--version', action='version', version='1.0')

        subparsers = parser.add_subparsers(help='commands')

        list_parser = subparsers.add_parser('list', help='List plugin info')
        list_parser = ListParser.make(parser=list_parser)

        version_parser = subparsers.add_parser('version', help='List this package version info')
        version_parser = VersionParser.make(parser=version_parser)

        return parser


class ListParser:
    __version__ = '1.0.2'

    @staticmethod
    def make(parser=CSArgParser()):
        parser.add_argument('-t', help='tab width (default=4)', default=4, type=int)
        parser.add_argument('--sort-by', help='attribute to sort by (default=name)', default='name')
        parser.add_argument('--sort-order', help='sort direction (default=ascending)', default='ascending')
        parser.add_argument('args', nargs='*', default=['Name', 'Category', 'Version', 'Description'])
        parser.set_defaults(func=list_print_wrapper)
        return parser


class VersionParser:
    __version__ = '1.0.1'

    @staticmethod
    def make(parser=CSArgParser()):
        parser.set_defaults(func=print_wrapper)

        return parser


def parser():
    return Parser.make()


__version__ = Parser.__version__
