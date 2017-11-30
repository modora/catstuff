import catstuff
from .config import try_get, load_yaml
from .path import expandpath
import os
import inspect

# PARSER IMPORTS
import pymongo

default_config_path = os.path.join(os.path.dirname(expandpath(catstuff.__file__)), 'config/default.yml')
default_config = load_yaml(default_config_path)
version = '1.0'  # config version


class _Config(dict):
    """ Allows monkey patching!! """
    pass


class GlobalParser:
    @staticmethod
    def parse(config=None):
        """ This is a convenience method to parse the config using all of the functions stored in this class"""
        out = _Config()

        out._config = config or {}
        for attr, func in inspect.getmembers(GlobalParser, predicate=inspect.isfunction):
            if attr is "parse":
                continue
            setattr(out, attr, func(config))  # all functions are assumed to contain a single argument
        return out

    @staticmethod
    def mongo_client(config):
        client_settings = try_get(config, ['mongodb', 'client'], default=default_config['mongodb']['client'])
        client = pymongo.MongoClient(**client_settings)
        return client

    @staticmethod
    def mongo_db(config):
        """ Returns the main database catstuff operates in"""
        client = GlobalParser.mongo_client(config)

        db_settings = try_get(config, ['mongodb', 'db'], default=default_config['mongodb']['db'])
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
