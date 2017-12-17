import os
import subprocess, platform
from glob import glob
from catstuff import tools, core
import pymongo


class CatStuffBaseTest:
    config_path = core.config.CSConfig.default_path

    @classmethod
    def setup_class(cls):
        core.init(config_path=cls.config_path)



class MongoBaseTest(CatStuffBaseTest):
    system = platform.system()
    conn_settings = {'serverSelectionTimeoutMS': 10000}
    '''
    Recommended that 'serverSelectionTimeoutMS' is at least 5 sec to allow for mongod to finish initializing
    '''

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
        conn = self.conn

        try:
            # The ismaster command is cheap and does not require auth.
            conn.admin.command('ismaster')
        except pymongo.errors.ConnectionFailure:
            print("Server not available")
            self.process.kill()

    def stop(self):
        # this is an unsafe shutdown but this is a test so i don't really care
        # if there is an existing mongod instance, I dont want to shut it down
        # if an existing mongod exists, the start process returns a returncode of 100 (fs lock is present) so
        # killing the start process will kill the errored start process
        self.process.kill()


class CSDBBaseTest(CatStuffBaseTest):
    mongo = MongoBaseTest()
    db_settings = {'name': 'catstuff_test'}

    @property
    def db(self):
        return pymongo.database.Database(self.mongo.conn, **self.db_settings)

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mongo.start()

    @classmethod
    def teardown_class(cls):
        cls.mongo.conn.close()
        cls.mongo.stop()

    def setup(self):
        pass

    def teardown(self):
        self.mongo.conn.drop_database(self.db_settings['name'])
