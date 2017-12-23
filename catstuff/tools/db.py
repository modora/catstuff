import pymongo


def unpack_mongo_details(pymongo_object):
    """ Convenience wrapper for unpacking mongodb objects"""

    def unpack_mongo_collection(collection: pymongo.collection.Collection):
        """ Returns the details necessary for establishing a connection to a collection"""
        coll = collection.name
        db = collection.database.name
        host, port = collection.database.client.address

        return host, port, db, coll

    def unpack_mongo_database(database: pymongo.database.Database):
        """ Returns the details necessary for establishing a connection to a database"""
        db = database.name
        host, port = database.client.address

        return host, port, db

    def unpack_mongo_connection(client: pymongo.MongoClient):
        """ Returns the details necessary for establishing a connection to a mongodb server"""
        return client.address

    return {
        pymongo.MongoClient: unpack_mongo_collection,
        pymongo.database.Database: unpack_mongo_database,
        pymongo.collection.Collection: unpack_mongo_collection,
    }[type(pymongo_object)](pymongo_object)


def link_data(uid, collection: pymongo.collection.Collection, src_coll=None) -> dict:
    # TODO: Needs to be reevaluated
    """
    Formats all the necessary data to link a mongo document to another mongo document
    :param uid: "_id" of the target document
    :param collection: the mongodb collection that the target document resides in
    :type: pymongo.collection._CSBaseCollection
    :param: src_coll: the mongodb collection that the source document resides in
    :type: (pymongo.collection._CSBaseCollection, None)
    :return: minimum connection settings needed to connect to the target collection
    :rtype: dict

    :Note: The return data is the **minimum** required connection settings. This shows the differences in the
    connection settings between the current collection and the target collection. If the target document is in the
    same collection, then the link_data will be an empty dictionary
    """

    if src_coll is None:
        # some random database that should never be created -- this should get overridden anyways
        src_coll = pymongo.MongoClient()['catstuff']['__catstuff_db_error']
    assert isinstance(src_coll, pymongo.collection.Collection)

    attrs = ('host', 'port', 'database', 'collection')
    data = {'_id': uid}
    for i, (other, current) in enumerate(zip(unpack_mongo_details(collection),
                                             unpack_mongo_details(src_coll))):
        if other != current:
            attr = attrs[i]
            data.update({attr: other})
    return data


def eval_link(src_data: pymongo.collection.Collection, link_data: dict, *args, **kwargs) -> (None, dict):
    """evaluates the lined document -- mongodb args are allowed"""
    host, port, db, coll = unpack_mongo_details(src_data)  # defaults

    host = link_data.get('host') or host
    port = link_data.get('port') or port
    db = link_data.get('database') or db
    coll = link_data.get('collection') or coll

    coll = pymongo.MongoClient(host, port)[db][coll]

    return coll.find_one({"_id": link_data['_id']}, *args, **kwargs)


def generate_uid(method):
    import bson, uuid

    try:
        return {
            'objectid': lambda : bson.ObjectId(),
            'uuid': lambda : str(uuid.uuid4())
        }[method]()
    except KeyError:
        raise NotImplementedError('Unknown method')


def test_connection(connection=None, *args, **kwargs):
    from pymongo.errors import ConnectionFailure

    client = pymongo.MongoClient(*args, **kwargs) if connection is None else connection
    assert isinstance(connection, pymongo.MongoClient)
    try:
        client.admin.command('ismaster')
    except ConnectionFailure:
        # should do logging here
        raise
