import os.path
import glob

# Import all files in this directory
modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

# Cleanup namespace
del glob
del os.path
del modules

from . import *

# BELOW IS TO GET PYCHARM TO STFU
from . import argparser
from . import common
from . import config
from . import db
from . import debug
from . import misc
from . import path
from . import plugins
from . import vars