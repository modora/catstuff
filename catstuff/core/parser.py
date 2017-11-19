import argparse, sys
from catstuff.tools.argparser import CSArgParser
from catstuff.core.manager import manager
from catstuff import __version__ as version

description = 'Core parser for catstuff'

parser = CSArgParser(description=description)

### GLOBAL SWITCHES
# None right now

parser.add_argument('action')

# these get passed to the action plugins
parser.add_argument('args', nargs=argparse.REMAINDER)
parser.add_argument('--version', action='version', version=version)

if __name__ == '__main__':
    args = parser.parse_args()
    action = manager.getPluginByName(name=args.action, category='Actions')
    if action is None:
        parser.error('unrecognized action {}'.format(args.action))
    else:
        action.plugin_object.main(args.args)