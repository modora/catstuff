from nose.tools import *
from catstuff.core.vars import VarPool, CSVarPool


class OtherPool(VarPool):
    pool = {}


def test_is_pool_empty():
    eq_(VarPool.dump(), {}, 'Varpool is not empty')


class TestCSVarPool:
    def teardown(self):
        CSVarPool.clear()

    def setup(self):
        CSVarPool.setup()

    def test_setup(self):
        CSVarPool.clear()

        app = 'catstuff'
        data = {
            'varpool': CSVarPool
        }

        CSVarPool.setup(data=data, app=app)
        for var, value in data.items():
            eq_(CSVarPool.get(var, app=app), value)


class TestMultiplePools:
    def teardown(self):
        VarPool.clear()
        OtherPool.clear()
        CSVarPool.clear()

    def test_pool_independence(self):
        """ pool attribute overwritten"""
        app = 'test'

        ok_(id(CSVarPool.pool) != id(OtherPool.pool), 'mem address of pools should be different')

        cs_pool = CSVarPool(app=app)
        other_pool = OtherPool(app=app)

        cs_pool.set('foo', 'bar')
        other_pool.set('hello', 'world')

        @raises(KeyError)
        def cs_pool_independence():
            cs_pool.get('hello', app=app)

        cs_pool_independence()

        @raises(KeyError)
        def other_pool_independence():
            other_pool.get('foo', app=app)

        other_pool_independence()

        ok_(CSVarPool.dump() != OtherPool.dump(), 'these pools should be different')

    def test_pool_dependence(self):
        """ pool attribute not overwritten"""
        ok_(id(CSVarPool.pool) == id(VarPool.pool), 'mem address of pools should be the same')

        var = 'foo'
        app = 'test'
        VarPool(app=app).set(var, 'bar')
        eq_(CSVarPool.get(var, app=app), 'bar')
        CSVarPool(app=app).set(var, 'foo')
        eq_(VarPool.get(var, app=app), 'foo')

