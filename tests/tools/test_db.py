from tests.common import *
from catstuff.tools import core, db
import pymongo


@raises(NotImplementedError)
def test_unknown_uid_gene_method():
    db.generate_uid('unknown method')


class TestCSCollection(CSDB):
    coll_name = 'test'

    def setup(self):
        super().setup()
        # using object attributes is a safe way of passing classes between the
        # test function
        self.obj = core.Collection(self.coll_name, db=self.db)

    def test_empty(self):
        assert_equal(self.obj.db.collection_names(), [], "Test database is not empty")

    def test_uid(self):
        uid = self.obj.uid
        result = self.obj.coll.find_one({"_id": uid})
        ok_(result is None, "UID is not unique")

    def test_insert(self):
        data = {'insert': 'method'}
        self.obj.insert(data)
        assert_equal({**data, **self.obj.pre_data}, self.obj.get())

    def test_standard_get(self):
        data = {'get': 'method', **self.obj.pre_data}
        self.obj.coll.insert_one(data)
        assert_equal(data, self.obj.get(), 'Standard get method failed')

    def test_get_default(self):
        # nothing should be in there right now
        result = self.obj.get(default='hello world')
        assert_equal(result, 'hello world', 'default result is different')

    def test_get_arg_passthru(self):
        data = {'123': 'abc'}
        self.obj.insert(data)
        doc = self.obj.get({"_id": 0})  # arg projection results in no id field returned
        assert_equal(doc, data, 'Something else was added to the predata')

        doc = self.obj.get(projection={"_id": 0})  # kwarg projection results in no id field returned
        assert_equal(doc, data, 'Something else was added to the predata')

    def test_delete(self):
        data = {'delete': 'method'}
        self.obj.coll.insert_one({**data, **self.obj.pre_data})
        ok_(self.obj.coll.find_one({"_id": self.obj.uid}) is not None,
            "Failed to insert document, unable to verify method")
        self.obj.delete()
        ok_(self.obj.get() is None, "Failed to delete document")

    def test_update(self):
        """ Same as test_insert"""
        data = {'update': 'method'}
        self.obj.update(data)
        assert_equal({**data, **self.obj.pre_data}, self.obj.coll.find_one({"_id": self.obj.uid}))

    def test_link_data(self):
        link_coll = pymongo.collection.Collection(self.obj.db, 'link')
        link_coll.insert_one({"_id": 123, 'foo': 'bar', 'linked': 'data'})
        link_data = self.obj.link_data(123, link_coll)
        data = {'source': 'document', 'link': link_data}
        self.obj.insert(data)

        doc = self.obj.get()
        assert_equal(doc, {
            '_id': self.obj.uid,
            'source': 'document',
            'link': {"_id": 123, 'collection': 'link'}
        }, 'Error encoding into databases')

        linked_doc = self.obj.eval_link(doc['link'])

        assert_equal(linked_doc, {"_id": 123, 'foo': 'bar', 'linked': 'data'})
