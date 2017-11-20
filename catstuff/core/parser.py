import argparse, sys
from catstuff.tools.argparser import CSArgParser
from catstuff.core.manager import CSPluginManager
from catstuff import __version__ as version


class CoreParser(CSArgParser):
    description = 'Core parser for catstuff'

    def __init__(self):
        super().__init__(description=self.description)
        # Core parser settings
        self.add_argument('--version', action='version', version=version)

        # action settings
        self.add_argument('action')
        self.add_argument('args', nargs=argparse.REMAINDER)


if __name__ == '__main__':
    parser = CoreParser()
    args = parser.parse_args()
    action = CSPluginManager().getPluginByName(name=args.action, category='Actions')
    if action is None:
        parser.error('unrecognized action {}'.format(args.action))
    else:
        action.plugin_object.main(args.args)