import catstuff.toolbox.modules as mods
import os
import hashlib, zlib
import math

__dir__ = os.path.dirname(__file__)
__mod__, __build__, _ = mods.importCore(os.path.join(__dir__, "checksum.plugin"))

_hashlib_methods = ['sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'blake2b', 'blake2s', 'md5',
                    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256']
_zlib_methods = ['crc32', 'adler32']


def checksum(file, method='md5', block_size=None, hex=True):
    '''
    Returns the checksum of a file
    :param file: path to file
    :param method: checksum algorithm
    :param block_size: Size of each chunk (Set to 'None' to assign defaults)
    :param hex: Return the hex digest
    :return:

    SHAKE methods return a 255 length string
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
    if method in _zlib_methods:
        h = m(b'')
    elif method in _hashlib_methods:
        h = m()
    elif method is None:
        raise KeyError('Unknown checksum method')
    else:
        raise NotImplementedError("method init not defined for {} method".format(method))

    if block_size is None:
        block_size = chuck_size(method)

    with open(file, 'rb') as file:
        for chunk in iter(lambda: file.read(block_size), b''):
            if method in _hashlib_methods:
                h.update(chunk)
            elif method in _zlib_methods:
                h = m(chunk, h)
            else:
                raise NotImplementedError("chunked-checksum method not defined for {} method".format(method))

    if method in _hashlib_methods:
        if method in ('shake_128', 'shake_256'):
            return h.hexdigest(255) if hex else h.digest(255)
        return h.hexdigest() if hex else h.digest()
    elif method in _zlib_methods:
        return format(h, 'x') if hex else h  # fix the else statement to byte object
    else:
        raise NotImplementedError("Return method not set for {} method".format(method))


def chuck_size(method):
    if method in _hashlib_methods:
        h = getattr(hashlib, method)()
        size = {
                         'some_method': 2 ** 8
                     }.get(method, 2**8) * h.block_size
        return size
    elif method in _zlib_methods:
        return 2 ** 16
    else:
        raise NotImplementedError("default block size not set for {} method".format(method))


class Checksum(mods.CSModule):
    def __init__(self):
        super().__init__(__mod__, __build__)

    def main(self, *args, **kwargs):
        raise NotImplementedError('Not implemented')