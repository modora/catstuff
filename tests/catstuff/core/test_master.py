from nose.tools import *
from tests.classes import CSDBBaseTest
from catstuff import core, tools


class TestMaster(CSDBBaseTest):
    def setup(self):
        super().setup()
        self.obj = core.dbs.CSMaster(db=self.db)

    @raises(AttributeError)
    def test_unset_path(self):
        print(self.obj.path)

    def test_insert(self):
        obj = self.obj
        obj.path = '/fake_path'
        data1 = obj.data(mod_name='mod1', data_={'foo': 'bar'})
        obj.insert(data1)
        data2 = obj.data(mod_name='mod2', data_={'hello': 'world'})
        obj.insert(data2)

        doc = obj.coll.find_one()
        data = {
            **obj.pre_data,
            **data1,
            **data2
        }
        assert_equal(doc, data)

    def test_get_raw(self):
        obj = self.obj

        assert_equal(obj.get_raw('123'), '123',
                     "Nothing should be in the db right now")

        obj.path = '/fake_path'
        data1 = obj.data(mod_name='mod1', data_={'foo': 'bar'})
        obj.insert(data1)
        data2 = obj.data(mod_name='mod2', data_={'hello': 'world'})
        obj.insert(data2)

        doc = obj.get_raw()
        data = {
            **obj.pre_data,
            **data1,
            **data2
        }
        assert_equal(doc, data)

    def test_get(self):
        obj = self.obj

        mod1 = core.dbs.CSCollection('mod1', database=self.db)
        mod2 = core.dbs.CSCollection('mod2', database=self.db)

        mod1.path = '/fake_path1'
        mod2.path = '/fake_path2'

        mod1.insert({"a": 'b'})
        mod2.insert({"1": '2'})

        data1 = mod1.get()
        data2 = mod2.get()

        obj.path = '/file_path'
        obj.insert(obj.data('mod1', obj.link_data(uid=data1["_id"], collection=mod1.coll)))
        obj.insert(obj.data('mod2', obj.link_data(uid=data2["_id"], collection=mod2.coll)))

        data = {
            'mod1': data1,
            'mod2': data2,
            **obj.pre_data
        }
        doc = obj.get()
        assert_equal(data, doc, "Master getter failed")