def import_all_files(recursive=False):
    from os.path import dirname, basename, isfile, join
    import glob
    if recursive:
        here = join(dirname(__file__), "**/*.py")
    else:
        here = join(dirname(__file__), "*.py")
    modules = glob.glob(here, recursive=recursive)
    restricted_files = {'__init__', '_core'}
    __all__ = [basename(f)[:-3] for f in modules if
               isfile(f) and not any(f.endswith(name + '.py') for name in restricted_files)]
    return __all__

__all__ = import_all_files()
from . import *
del import_all_files

from .common import *

# This code is redundant, the from . import * does the same but i want the IDE to stfu
from . import argparser
from . import common
from . import config
from . import config_parser
from . import db
from . import debug
from . import misc
from . import path
from . import plugins
from . import vars