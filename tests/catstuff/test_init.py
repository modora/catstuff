from nose.tools import *
import catstuff


def setup():
    catstuff.core.init()


def test_is_config_defined():
    try:
        config = catstuff.core.vars.CSVarPool.get('config', 'catstuff')
    except KeyError:
        ok_(False, 'Plugin manager not defined')
        raise

    ok_(isinstance(config, catstuff.core.config.CSConfig), 'unexpected config found')


def test_is_manager_defined():
    try:
        manager = catstuff.core.vars.CSVarPool.get('manager', 'catstuff')
    except KeyError:
        ok_(False, 'Plugin manager not defined')
        raise

    ok_(isinstance(manager, catstuff.core.plugins.CSPluginManager), 'unexpected plugin manager found')

