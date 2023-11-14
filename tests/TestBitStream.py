from BitStream import BitStreamReader, BitStreamWriter
import unittest
import random


class TestBitStream(unittest.TestCase):

    def test_write_read(self):
        expected = random.randbytes(10000)
        with BitStreamWriter('test.txt') as f:
            for byte in expected:
                f.write(byte, 8)
        actual = []
        with BitStreamReader('test.txt') as f:
            while not f.is_eof():
                actual.append(f.read(8))
        self.assertSequenceEqual(expected, actual)
