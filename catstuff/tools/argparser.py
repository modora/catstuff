import argparse, sys

__version__ = '1.0.2'


class CSArgParser(argparse.ArgumentParser):
    """ Argument parser that shows help if there is an error """
    def error(self, message, exit=False):
        sys.stderr.write('Error: {}\n'.format(message))
        self.print_help()
        if exit:
            sys.exit(2)
