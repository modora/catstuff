import traceback, shutil, time
import logging  # replace with logger
from catstuff.core.manager import CSPluginManager, MissingPluginException
from catstuff.core.vars import CSVarPool
from catstuff.core.parser import CoreArgParser
from catstuff.core.config import Config
import catstuff.tools as tools

app = 'catstuff'


def setup(config_path: str=None):
    def init_config(path: str=None):
        if path is None:
            try:
                return Config.load_default()
            except FileNotFoundError:
                tools.path.touch(Config.default_path)
                return Config({})
        else:
            return Config.load_config(path)

    CSVarPool.clear()
    vars_ = CSVarPool(app=app)
    vars_.set('manager', CSPluginManager())
    vars_.set('config', init_config(config_path))



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