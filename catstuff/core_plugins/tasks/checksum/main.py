import collections
import hashlib
import zlib

from catstuff import core

from .config import mod_name, build

hashlib_methods = {'sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'md5',
                    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256'}
zlib_methods = {'crc32', 'adler32'}


def checksum(file, method='md5', block_size=None, hex=True) -> str:
    '''
    Returns the checksum of a file
    :param file: path to file
    :param method: checksum algorithm
    :param block_size: Size of each chunk (Set to 'None' to assign defaults)
    :param hex: Return the hex digest
    :return:
    :rtype: str
    '''

    m = {
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha224': hashlib.sha224,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'blake2b': hashlib.blake2b,
        'blake2s': hashlib.blake2s,
        'md5': hashlib.md5,
        'sha3_224': hashlib.sha3_224,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512,
        'shake_128': hashlib.shake_128,
        'shake_256': hashlib.shake_256,
        'crc32': zlib.crc32,
        'adler32': zlib.adler32
    }.get(method, lambda: None)
    if method in zlib_methods:
        h = m(b'')
    elif method in hashlib_methods:
        h = m()
    else:
        raise NotImplementedError("{} method not defined".format(method))

    if block_size is None:
        block_size = chunk_size(method)

    with open(file, 'rb') as file:
        for chunk in iter(lambda: file.read(block_size), b''):
            if method in hashlib_methods:
                h.update(chunk)
            elif method in zlib_methods:
                h = m(chunk, h)
            else:
                raise NotImplementedError("chunked-checksum method not defined for {} method".format(method))

    if method in hashlib_methods:
        if method in ('shake_128', 'shake_256'):
            return h.hexdigest(64) if hex else h.digest(64)
        return h.hexdigest() if hex else h.digest()
    elif method in zlib_methods:
        return format(h, 'x') if hex else h  # fix the else statement to byte object
    else:
        raise NotImplementedError("Return method not set for {} method".format(method))


def chunk_size(method):
    # TODO: Optimizer -- work on this later
    if method in hashlib_methods:
        h = getattr(hashlib, method)()
        size = {
                         'some_method': 2 ** 8
                     }.get(method, 2**8) * h.block_size
        return size
    elif method in zlib_methods:
        return 2 ** 16
    else:
        raise NotImplementedError("default block size not set for {} method".format(method))


class Checksum(core.plugins.CSTask, core.dbs.CSCollection):
    def __init__(self):
        core.plugins.CSTask.__init__(self, mod_name, build)
        core.dbs.CSCollection.__init__(self, mod_name)

    @staticmethod
    def data(path, methods, block_size=None, hex=True):
        d = {}
        assert isinstance(methods, collections.Iterable)
        methods = {methods} if isinstance(methods, str) else methods
        for method in methods:
            d[method] = checksum(path,  method=method, block_size=block_size, hex=hex)
        return d

    def main(self, path, methods='md5', block_size=None, hex=True, **kwargs):
        self.path = path  # path getter will return an error if path is not defined set
        data = self.data(self.path, methods=methods, block_size=block_size, hex=hex)

        self.replace(data)
        return data
