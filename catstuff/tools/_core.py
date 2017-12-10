""" This is a controlled way to import stuff from outside of this package"""

from catstuff.core.tools import *
from catstuff.core.dbs import test_connection, CSMaster, CSMongoCollection, generate_uid, eval_link, link_data
from catstuff.core.plugin_categories import CSAction, CSTask, StrMethod
from catstuff.core.vars import VarPool