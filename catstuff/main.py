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


def exec_action(action, args, debug=False):
    try:
        action = core.vars.CSVarPool.get('manager', app='catstuff').getPluginByName(name=action, category='Action')
        if action is None:  # plugin does not exist
            raise core.plugins.MissingPluginException('unrecognized action {}'.format(action))
        action.plugin_object.main(args)
    except Exception as e:
        if debug:
            traceback.print_exc()
            time.sleep(0.1)  # wait until traceback finishes printing
            # probably a smarter way to wait but w/e

            cols = shutil.get_terminal_size()[0]
            print("-" * cols)
            CoreArgParser().error(e, exit=True)


def main():
    parser = CoreArgParser()
    args = parser.parse_args()

    if args.debug:
        # TODO: Implement logger
        # logging.basicConfig(level=logging.DEBUG)
        pass

    core.init(config_path=args.config)
    exec_action(args.action, args.args, debug=args.debug)


if __name__ == '__main__':
    main()