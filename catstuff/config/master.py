from catstuff.tools.config import try_get
import pymongo


class SettingsContainer:
    default_args = {}
    default_kwargs = {}

    @property
    def settings(self):
        return {**self.default_args, **self.default_kwargs}


class Client(SettingsContainer):
    pass


class DB(SettingsContainer):
    default_args = {'name': 'catstuff'}


default_client = Client()
default_db = DB()


def parser(config):
    client_settings = try_get(config, ['master', 'client'], default=default_client)
    db_settings = try_get(config, ['master', 'db'], default=default_db)

    for key in default_client.settings:
        if key not in client_settings:
            raise KeyError("Missing required key: {}".format(".".join(['master', 'client', key])))
    for key in default_db.settings:
        if key not in db_settings:
            raise KeyError("Missing required key: {}".format(".".join(['master', 'db', key])))

    client = pymongo.MongoClient(**client_settings)
    db = pymongo.database.Database(client, **db_settings)
    return db