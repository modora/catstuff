import traceback, shutil, time
import logging  # replace with logger
import argparse
import catstuff

from catstuff import core, tools

class CoreArgParser(tools.argparser.CSArgParser):
    description = 'Core parser for catstuff'

    def __init__(self):
        super().__init__(description=self.description)
        # Core parser settings
        self.add_argument('--version', action='version', version=catstuff.__version__)
        self.add_argument('--debug', action='store_true', default=False, help='Sets verbosity to debug')
        self.add_argument('--config', type=str, default=core.config.CSConfig.default_path)

        # action settings
        self.add_argument('action')
        self.add_argument('args', nargs=argparse.REMAINDER)


def main():
    parser = CoreArgParser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig()

    core.init(config_path=args.config)

    try:
        action = core.vars.CSVarPool.get('manager', app=app).getPluginByName(name=args.action, category='Action')
        if action is None:  # plugin does not exist
            raise core.plugins.MissingPluginException('unrecognized action {}'.format(args.action))
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