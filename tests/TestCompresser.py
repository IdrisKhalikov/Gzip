import unittest
import random
import pygzip
import shutil
import os

class TestCompresser(unittest.TestCase):

    def test_compress_and_decompress(self):
        text = random.randbytes(10000)
        with open('test.txt', 'wb') as f:
            f.write(text)
        pygzip.compress('test.txt')
        os.remove('test.txt')
        pygzip.decompress('test.archive.gz')
        os.remove('test.archive.gz')
        actual = bytearray()
        with open('test/test.txt', 'rb') as f:
            actual.extend(f.read())
        shutil.rmtree('test')
        self.assertSequenceEqual(text, actual)