import unittest
from Crc32 import Crc32

class CrcTest(unittest.TestCase):
    
    def test_crc_add(self):
        crc = Crc32()
        for byte in b'Hello world!':
            crc.add(byte)
        self.assertEqual(crc.get_crc(), 0x1b851995)
    
    def test_crc_add_range(self):
        crc = Crc32()
        crc.add_bytes(b'Hello world!')
        self.assertEqual(crc.get_crc(), 0x1b851995)

    def test_crc_get_multiple(self):
        crc = Crc32()
        crc.add_bytes(b'Hello ')
        self.assertEqual(crc.get_crc(), 0xea2dfcc0)
        crc.add_bytes(b'world!')
        self.assertEqual(crc.get_crc(), 0x1b851995)