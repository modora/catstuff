from nose.tools import *

import tests
from tests import files

from catstuff.core_plugins.tasks.checksum.checksum.main import *


@raises(NotImplementedError)
def test_unknown_method_123():
    checksum(files.empty_file, method=123)


@raises(NotImplementedError)
def test_unknown_method_None():
    checksum(files.empty_file, method=None)


def test_filled_sha1():
    actual = 'e904e143809b8ee161abdc55455bd5ff7773b5d7'.lower()
    result = checksum(files.filled_file, method='sha1').lower()
    assert_equal(result, actual)


def test_empty_sha1():
    actual = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'.lower()
    result = checksum(files.empty_file, method='sha1').lower()
    assert_equal(result, actual)


class Library:
    skip_methods = set()

    def __init__(self, file, actuals={}):
        self.file = file

        for actual in actuals:
            setattr(self, actual, actuals[actual])

    @nottest
    def test_method(self, method):
        actual = getattr(self, method, None)
        if method in self.skip_methods:
            return
        if actual is None:
            ok_(False, 'Checksum could not be verified')
        result = checksum(self.file, method=method)
        assert_equal(result.lower(), actual.lower())


class Zlib(Library):
    def test_crc32(self):
        self.test_method('crc32')

    def test_adler32(self):
        self.test_method('adler32')


class Hashlib(Library):
    skip_methods = {'blake2b', 'blake2s'}  #  cannot verify these right now

    def test_sha1(self):
        self.test_method('sha1')

    def test_sha256(self):
        self.test_method('sha256')

    def test_sha224(self):
        self.test_method('sha224')

    def test_sha384(self):
        self.test_method('sha384')

    def test_sha512(self):
        self.test_method('sha512')

    def test_blake2b(self):
        self.test_method('blake2b')

    def test_blake2s(self):
        self.test_method('blake2s')

    def test_md5(self):
        self.test_method('md5')

    def test_sha3_224(self):
        self.test_method('sha3_224')

    def test_sha3_256(self):
        self.test_method('sha3_256')

    def test_sha3_384(self):
        self.test_method('sha3_384')

    def test_sha3_512(self):
        self.test_method('sha3_512')

    def test_shake_128(self):
        self.test_method('shake_128')

    def test_shake_256(self):
        self.test_method('shake_256')


class TestFilled(Hashlib, Zlib):
    actuals = {
        'sha1'     : 'e904e143809b8ee161abdc55455bd5ff7773b5d7',
        'sha224'   : '0e06806c50baf975474d31dbd74eb394aee928c034c191d91dfc65dc',
        'sha256'   : '0191f9186550a8e8e0b3c4112757da13d1434d20f1ca7c3a1b2d1e4119301951',
        'sha384'   : 'c2e19786394a1924fa9086339581a22e7946d0b7834ec55750b32fe59b49c6748f64ecab20561722ff6ca2ac7a60ef39',
        'sha512'   :
            '52936535a745013a6f1f2721f511f81530255569bf0682d50f30b9ce67c3ec5745b1bfe72142540f5f2d629984f1638ed8d6c0e8f86da57975dc202fa320d528',
        # 'blake2b': '123',
        # 'blake2s': '0168617AC4EBBD41BD461991C4F28871457F3ECBFBSDllF4363E4AA81EFC43AF',
        'md5'      : 'a5ed84a3e65b4cdb086fc9d4aa0c9a45',
        'sha3_224' : 'a942c6d8d4103b136ff0b606a8095fad16b3b6bce76e78227c3df14f',
        'sha3_256' : '38920b162fd995c3325b0b5b96e5b0068c05727de6983941b8fe89de9e195d28',
        'sha3_384' : '49a2ea29ad16820a0c2845904f10a89d9dcade25786d97df4b245b58f7963b1cb5bb88df77d7095405455d9452b95564',
        'sha3_512' :
            'c34069059313d61a3030479ad9bff8cfc4308322840e8376dc9c6117bb3e39e47217bec789e1cfd8ebac61f059174352722c870b24b6b2800ed635f43e1ef285',
        'shake_128': '0cf15a6a82525b3abd3cf74a99d8302fd44adb70333ff4db932080643591f4eea92ec63edcda1fb319f504bbcdf53014e5e7abfa6feb59060332b0a484775efa',
        'shake_256': '4f35797528ece0c72d552b53eccc3e8c6a0ea3c1751008404b276978c572bd4e6fb1d2a06fd65c25291cf06855699213d4adce7d8702ed4f1b20a7c48b3fbcf1',
        'crc32': 'f11b4ef9',
        'adler32': '2bb91434'
    }

    def __init__(self):
        Library.__init__(self, files.filled_file, actuals=self.actuals)


class TestPlugin(tests.classes.CSDBBaseTest):
    def setup(self):
        self.obj = Checksum()

    def test_main(self):
        pass # TODO: test this