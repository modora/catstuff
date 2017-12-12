import traceback, shutil, time
import logging  # replace with logger
from catstuff.core.manager import CSPluginManager, MissingPluginException
from catstuff.core.vars import CSVarPool
from catstuff.core.parser import CoreArgParser

app = 'catstuff'


def setup():
    CSVarPool.clear()
    vars_ = CSVarPool(app=app)
    vars_.set('manager', CSPluginManager())


def main():
    parser = CoreArgParser()
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig()

    setup()

    try:
        action = CSVarPool.get('manager', app=app).getPluginByName(name=args.action, category='Action')
        if action is None:  # plugin does not exist
            raise MissingPluginException('unrecognized action {}'.format(args.action))
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