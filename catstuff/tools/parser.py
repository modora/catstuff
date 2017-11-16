import argparse, sys


class CSArgParser(argparse.ArgumentParser):
    """ Argument parser that shows help if there is an error """
    def error(self, message):
        sys.stderr.write('Error: {}\n'.format(message))
        self.print_help()
        sys.exit(2)