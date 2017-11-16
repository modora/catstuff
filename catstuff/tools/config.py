import yaml
import pymongo

def load_config(path):
    try:
        return yaml.load(open(path, 'r'))
    except yaml.YAMLError as e:
        print("Error trying to load {path}: {error}".format(path=path, error=e))

def get_leaves(config):
    """
    Returns the end-keys of a dictionary
    :param config:
    :return:

    :Example:

    >>> config = {
        'key1': 1,
        'key2': {
            'nested_key1': 'n1',
            'nested_key2': 'n2'
        }
    }
    >>> get_leaves(config)
    ['key1', 'key2.nested_key1', key2.nested_key2']
    """
    pass

def eval_leaf(config, leaf: list):
    """
    Evalueates the value of a key (or subkey) within a dictionary
    :param config:
    :param leaf:
    :return:

    :raise KeyError: key does not exist in config
    """
    conf = config
    if isinstance(leaf, str):
        leaf = leaf.split('.')
    for key in leaf:
        conf = conf[key]
    return conf

def get_db_settings(config: dict, default_db=None):
    """
    Returns db settings
    :param config:
    :param default_db: Default db setting if setting not found
    :return: (host, port, name)
    :rtype: tuple
    """
    if default_db is None:
        conn = pymongo.MongoClient(host='localhost', port=27017)
        default_db = pymongo.database.Database(conn, name='catstuff')
    else:
        assert isinstance(default_db, pymongo.database.Database)

    default_db_name = default_db.name
    (default_host, default_port) = default_db.client.address

    db = config.get('db', {})
    host = db.get('host', default_host)
    port = db.get('host', default_port)
    name = db.get('host', default_db_name)

    return (host, port, name)
