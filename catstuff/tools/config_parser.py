import catstuff
from catstuff import tools
from catstuff.tools.config import try_get
import os
import pymongo

default_config_path = os.path.join(os.path.dirname(tools.path.expandpath(catstuff.__file__)), 'config/default.yml')
default_config = tools.config.load_yaml(default_config_path)
version = '1.0'  # config version


class GlobalParser:
    @staticmethod
    def master(config):
        """ Returns the master db settings"""
        client_settings = try_get(config, ['master', 'client'], default=default_config['master']['client'])
        db_settings = try_get(config, ['master', 'db'], default=default_config['master']['db'])

        client = pymongo.MongoClient(**client_settings)
        db = pymongo.database.Database(client, **db_settings)
        return db

    @staticmethod
    def version(config):
        """ Returns the config version"""
        # this function will be more useful later if the config format changes
        # If the format is changed, then each of the methods defined will just
        # need a switch based on the config version
        return try_get(config, 'version', default=version)

    @staticmethod
    def resources(config):
        """ Returns system resource limit settings"""
        NotImplementedError("Have yet to set a resource limitter")

    @staticmethod
    def importer(config):
        return try_get(config, 'importer', default=default_config['importer'])


class LocalParser:
    @staticmethod
    def tasks(config):
        return try_get(config, 'tasks', default=[])

    @staticmethod
    def plugins(config, plugin=None):
        if plugin:
            return try_get(config, ['plugins', plugin], default=[])
        else:
            return try_get(config, ['plugins'], default=[])
