from os.path import dirname
import os

test_basedir = dirname(__file__)
empty_file = os.path.join(test_basedir, 'files/empty.file')
filled_file = os.path.join(test_basedir, 'files/filled.file')