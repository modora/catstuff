import os
from datetime import datetime
import fnmatch
import logging
import uuid
import argparse
import pymongo
from distutils.version import StrictVersion

import db

__version__ = '0.1.0'

def timestamp(time):
    '''Converts from sec since epoch to human readable timestamp (UTC)'''
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.fromtimestamp(time))


def expand_path(path):
    return os.path.expandvars(os.path.expanduser(path))


def path_filter(path, include_pattern=['*'], exclude_pattern=[]):
    ''' Returns a boolean whether the path should be included '''

    if True in [True for inc in include_pattern if fnmatch.fnmatchcase(path, inc)] and \
       True not in [True for exc in exclude_pattern if fnmatch.fnmatchcase(path, exc)]:
        return True
    else:
        return False


def get_filelist(top,
                 include=['*'], exclude=[], followlinks=False, max_depth=0):
    '''
    Recursively gets the filepath of all files within some top level directory

    :param top: 'str/path/to/dir'
    :param include: [list, of, include, patterns]
    :param exclude: [list, of, exclude, patterns]
    :param followlinks: boolean
        follow symlinks?
    :param max_depth: int
        top is depth 0
    :return: list
    '''

    filelist = []
    depth_offset = top.rstrip(os.path.sep).count(os.path.sep)

    exclude_dirs = [expand_path(ex) for ex in exclude if ex[-1] is os.path.sep]
    exclude_files = [expand_path(ex) for ex in exclude if ex not in exclude_dirs]
    include_dirs = [expand_path(inc) for inc in include if inc[-1] is os.path.sep]
    include_files = [expand_path(inc) for inc in include if inc not in include_dirs]

    for root, dirs, files in os.walk(top, followlinks=followlinks):
        depth = root.count(os.path.sep) - depth_offset
        if depth == max_depth:
            del dirs[:]
        for i, dir in enumerate(dirs):
            if path_filter(dir, include_dirs, exclude_dirs):
                del dirs[i]
        for file in files:
            f = os.path.join(root, file)
            if path_filter(f, include_files, exclude_files):
                filelist.append(f)
    return filelist


class FileIndex(db.CSCollection):
    collection = 'index'
    __version__ = '1.0.0'

    indexes = [
        {
            'name': 'path',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: path
        },
        {
            'name': 'inode',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: os.stat(path).st_ino
        },
        {
            'name': 'device',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: os.stat(path).st_dev
        },
        {
            'name': 'size',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: os.stat(path).st_size
        },
        {
            'name': 'mod_time',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: os.stat(path).st_mtime
        },
        {
            'name': 'index_version',
            'type': pymongo.ASCENDING,
            'opts': None,
            'data': lambda path: __version__
        }
    ]
    keys = []
    for _i in indexes:
        keys.append(_i['name'])

    def __init__(self):
        super().__init__(self.collection)

    def data(self, path):
        d = {}

        for i in self.indexes:
            d[i.get('name')] = i.get('data')(path)
        return d

    def update_existing(self):
        for doc in self.coll.find():
            doc.upd

            # update if outdated version
            if StrictVersion(self.__version__) > StrictVersion(doc['version']):

    def add_one(self, path):
        d = self.data(path)
        if self.coll.find_one
        self.index.find_one_and_update

        self.index.update_one

        db_data = self.coll.find_one({"_id": self.uid})  # existing data
        if db_data is not None:
            if self.version != db_data['version']:
                action = 'Replace'
            else:
                action = 'Skip'
        else:
            action = 'Insert'


        self.coll.update_many(qry, {'$set': d}, upsert=True)


class UID(Index):
    logging.basicConfig(
        format='(uid: %(uid)) %(message)'
    )

    def __init__(self, uid=None):
        super().__init__()

    @staticmethod
    def generate_uid():
        ''' Return a uid in hex form'''
        return uuid.uuid4().hex

    def _debug(self, msg, *args, **keywords):
        logging.debug(msg, uid=self.uid, *args, **keywords)

    def _warning(self, msg, *args, **keywords):
        logging.warning(msg, uid=self.uid, *args, **keywords)

    def _info(self, msg, *args, **keywords):
        logging.info(msg, uid=self.uid, *args, **keywords)

    def _error(self, msg, *args, **keywords):
        logging.error(msg, uid=self.uid, *args, **keywords)

    def _uid_none(self, uid):
        '''
        returns the uid if not defined
        this is mostly a macro for most functions
        '''
        if uid is None:
            return self.uid
        return uid

    def set_uid(self, uid=None):
        if uid is None:
            self.uid = self.generate_uid()
        else:
            self.uid = uid

    def get(self):
        return self.coll.find_one({"_id": self.uid})

    def add(self, path, _):
        ''' Add data to index'''

        if self.uid is None:
            self.uid = self.generate_uid()

        super().add(path, {"_id": self.uid})

    def check_status(self):
        '''
        Returns one of the following states:
            'missing'
            'updated'
            'none' (no change)
        '''

        if self.check_missing():
            return 'missing'
        elif self.check_updated():
            return 'updated'
        return 'none'

    def check_missing(self):
        data = self.get()
        if os.path.exists(data['path']):
            self._info('Missing path {}'.format(data['path']))
            return True
        return False

    def check_updated(self):
        data = self.get()
        if data['size'] != os.stat(data['path']).st_size:
            self._debug('File size changed from {old_size} B to {new_size} B'.format(
                old_size=data['size'], new_size=os.stat(data['path']).st_size
            ))
        elif data['mod_time'] != os.stat(data['path']).st_mtime:
            self._debug('Mod time changed from {old_time} to {new_time}'.format(
                old_time=data['mod_time'], new_time=os.stat(data['path']).st_mtime
            ))

    def delete(self, uid=None):
        ''' Removes an element from the index'''
        uid = self._uid_none(uid)
        self.coll.delete({"_id": uid})

    def remove(self, uid=None):
        ''' alias for delete'''
        self.delete(uid)

    def update(self, uid=None):
        ''' Upserts data into a collection '''
        uid = self._uid_none(uid)
        data = self.get()
        if data is not None:
            path = data['path']
            self.add(path, uid)


def parser():
    p = argparse.ArgumentParser()
    p.add_argument('path', help='The path to import into index')
    p.add_argument('-d', '--depth', help="max search depth", default='0', type=int)
    p.add_argument('-v', '--verbose', action='count')
    p.add_argument('--debug', action='store_true')

    return p.parse_args()


def main(path, depth=0):
    filelist = get_filelist(path, max_depth=depth)
    for file in filelist:
        index = Index()
        index.set_uid()
        print('Adding {path} to db'.format(path=file))
        index.uid.add(file)


if __name__ == '__main__':
    args = parser()

    if args.debug is True or args.verbose >=3:
        logging.Logger(name='index', level=logging.DEBUG)

    main(args.path,
         depth=args.depth)