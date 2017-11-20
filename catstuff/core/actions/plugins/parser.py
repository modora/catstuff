from argparse import ArgumentParser
from catstuff.tools.argparser import CSArgParser
from catstuff.core.actions.plugins.list import print_wrapper as list_print_wrapper
from catstuff.core.actions.plugins.version import print_wrapper as version_print_wrapper


def _default_parser(**parser):
    try:
        parser = parser['parser']
    except KeyError:
        parser = CSArgParser()
    return parser


class Parser:  # Errors occur in adding the subparser when using class inheritance
    # Main parser
    __version__ = '1.0'

    @staticmethod
    def make(**parser):  # constructs the parser
        parser = _default_parser(**parser)

        parser.add_argument('--version', action='version', version='1.0')

        subparsers = parser.add_subparsers(help='commands')

        list_parser = subparsers.add_parser('list', help='List plugin info')
        list_parser = ListParser.make(parser=list_parser)

        version_parser = subparsers.add_parser('version', help='List this package version info')
        version_parser = VersionParser.make(parser=version_parser)

        return parser


class ListParser:
    __version__ = '1.0'

    @staticmethod
    def make(**parser):
        parser = _default_parser(**parser)

        parser.add_argument('-t', help='tab size', default=4, type=int)
        parser.add_argument('args', nargs='*', default=['Name', 'Category' ,'Version', 'Description'])
        parser.set_defaults(func=list_print_wrapper)
        return parser


class VersionParser:
    __version__ = '1.0'

    @staticmethod
    def make(**parser):
        parser = _default_parser(**parser)
        parser.set_defaults(func=version_print_wrapper)

        return parser


def parser():
    return Parser.make(parser=CSArgParser())

