from catstuff.tools.argparser import CSArgParser
import catstuff.core.actions.plugins2.list

# class Parser(CSArgParser):
#     __version__ = '1.0'  # parser version


# class ListParser(CSArgParser):
#     __version__ = catstuff.core.actions.plugins.list.__version__  # list version
#
#     def __init__(self):
#         super().__init__()
#         self.add_argument('-t', help='tab size', default=4, type=int)
#         self.add_argument('args', nargs='*', default=['Name', 'Version', 'Description'])
#         self.set_defaults(func=catstuff.core.actions.plugins.list.print_wrapper)
#
#
# class VersionParser(CSArgParser):
#     __version__ = catstuff.core.actions.plugins.version.__version__  # version parser version
#
#     def __init__(self):
#         super().__init__()
#         self.set_defaults(func=catstuff.core.actions.plugins.version.print_versions)

parser = CSArgParser()
parser.add_argument('--version', action='version', version='1.0')

subparsers = parser.add_subparsers(help='commands')

list_parser = subparsers.add_parser('list', help='List plugin info')
list_parser.add_argument('-t', help='tab size', default=4, type=int)
list_parser.add_argument('args', nargs='*', default=['Name', 'Version', 'Description'])
list_parser.set_defaults(func=catstuff.core.actions.plugins.list.print_wrapper)

version_parser = subparsers.add_parser('version', help='List this package version info')
version_parser.set_defaults(func=catstuff.core.actions.plugins.version.print_versions)
