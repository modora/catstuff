import traceback, shutil, time
from catstuff.core.manager import CSPluginManager
from catstuff.core.vars import VarPool
from .parser import CoreArgParser

app = 'catstuff'
parser = CoreArgParser()


def setup():
    VarPool.reset()
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