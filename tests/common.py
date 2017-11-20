from os.path import dirname
import os
import subprocess, platform
import pymongo
from glob import glob
from catstuff.tools.db import *


test_basedir = dirname(__file__)
empty_file = os.path.join(test_basedir, 'files/empty.file')
filled_file = os.path.join(test_basedir, 'files/filled.file')


class Mongo:
    system = platform.system()
    conn_settings = {'serverSelectionTimeoutMS': 1000}

    @property
    def conn(self):
        return pymongo.MongoClient(**self.conn_settings)

    def start(self, quiet=True):
        """ Opens up mongod"""
        std_out = open(os.devnull, 'w') if quiet else None

        if self.system == 'Windows':
            try:
                path = glob(r"C:\Program Files\MongoDB\**\mongod.exe", recursive=True)[0]
            except IndexError:
                raise FileNotFoundError("Mongod.exe not found. Is MongoDB installed?")
        else:
            raise NotImplementedError('{} not supported (yet??)'.format(self.system))
        self.process = subprocess.Popen(path, stdout=std_out)
        conn = self.conn  # wait until daemon is ready to listen
        conn.close()

    def stop(self):
        # this is an unsafe shutdown but this is a test so i don't really care
        # if there is an existing mongod instance, I dont want to shut it down
        # if an existing mongod exists, the start process returns a returncode of 100 (fs lock is present) so
        # killing the start process will kill the errored start process
        self.process.kill()


class CSDB():
    mongo = Mongo()
    db_settings = {'name': 'catstuff_test'}

    @property
    def db(self):
        return pymongo.database.Database(self.mongo.conn, **self.db_settings)

    @classmethod
    def setup_class(cls):
        cls.mongo.start()

    @classmethod
    def teardown_class(cls):
        cls.mongo.conn.close()
        cls.mongo.stop()

    def setup(self):
        pass

    def teardown(self):
        self.mongo.conn.drop_database(self.db_settings['name'])
