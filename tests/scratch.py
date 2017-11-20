from nose.tools import *
from .common import *
from catstuff.tools.db import *
import pymongo

mongo = Mongo()
connection = pymongo.MongoClient(serverSelectionTimeoutMS=1000)

# def setup_module(module):
#     print('mongod start')
#     mongo.start()
#
# def teardown_module(module):
#     print('mongod stop')
#     mongo.stop()

class TestClass:
    db_name = 'test'

    @classmethod
    def setup_class(cls):
        print('')
        print("Runnign TestClass class setup")
        mongo.start(quiet=False)


    @classmethod
    def teardown_class(cls):
        print('')
        print("Runnign TestClass class teardown")
        mongo.stop()

    def setup(self):
        print('')
        print("Runnign TestClass setup")
        global obj
        db = pymongo.database.Database(connection, self.db_name)
        obj = Collection('test', db=db)

    def teardown(self):
        print('')
        print("Runnign TestClass teardown")
        connection.drop_database(self.db_name)

    def test1(self):
        print('')
        print("This is test1")
        ok_(True)

    def test2(self):
        print('')
        print("This is test2")
        ok_(isinstance(obj, Collection))

    def test_insert(self):
        obj.insert({'1': 1})