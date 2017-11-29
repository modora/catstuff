import argparse, traceback, shutil, time, sys
from catstuff.core.manager import CSPluginManager
from catstuff.core.vars import VarPool
import catstuff

__version__ = '1.0.2'


class CSArgParser(argparse.ArgumentParser):
    """ Argument parser that shows help if there is an error """
    def error(self, message, exit=False):
        sys.stderr.write('Error: {}\n'.format(message))
        self.print_help()
        if exit:
            sys.exit(2)


class CoreArgParser(CSArgParser):
    description = 'Core parser for catstuff'

    def __init__(self):
        super().__init__(description=self.description)
        # Core parser settings
        self.add_argument('--version', action='version', version=catstuff.__version__)
        self.add_argument('--debug', action='store_true', default=False, help='Sets verbosity to debug')

        # action settings
        self.add_argument('action')
        self.add_argument('args', nargs=argparse.REMAINDER)

app = 'catstuff'
parser = CoreArgParser()


def setup():
    vars_ = VarPool(app=app)
    vars_.set('manager', CSPluginManager())


def main():
    args = parser.parse_args()
    setup()

    vars_ = VarPool()

    try:
        action = vars_.get('manager', app=app).getPluginByName(name=args.action, category='Action')
        if action is None:  # plugin does not exist
            raise AttributeError('unrecognized action {}'.format(args.action))
        action.plugin_object.main(args.args)
    except Exception as e:
        if args.debug:
            traceback.print_exc()
            time.sleep(0.1)  # wait until traceback finishes printing
            # probably a smarter way to wait but w/e

            cols = shutil.get_terminal_size()[0]
            print("-" * cols)
        parser.error(e, exit=True)


if __name__ == '__main__':
    main()