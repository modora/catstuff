import argparse, traceback, shutil, time
from catstuff.tools.argparser import CSArgParser
from catstuff.core.manager import CSPluginManager
from catstuff import __version__ as version


class CoreParser(CSArgParser):
    description = 'Core parser for catstuff'

    def __init__(self):
        super().__init__(description=self.description)
        # Core parser settings
        self.add_argument('--version', action='version', version=version)
        self.add_argument('--debug', action='store_true', default=False, help='Sets verbosity to debug')

        # action settings
        self.add_argument('action')
        self.add_argument('args', nargs=argparse.REMAINDER)

def main():
    parser = CoreParser()
    args = parser.parse_args()
    action = CSPluginManager().getPluginByName(name=args.action, category='Action')
    try:
        action.plugin_object.main(args.args)
    except AttributeError:
        if args.debug:
            traceback.print_exc()
            time.sleep(0.1)  # wait until traceback finishes printing
            # probably a smarter way to wait but w/e

            cols = shutil.get_terminal_size()[0]
            print("-" * cols)
        parser.error('unrecognized action {}'.format(args.action))


if __name__ == '__main__':
    main()