import argparse, sys
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
