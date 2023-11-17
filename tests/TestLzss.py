import unittest
import Lzss

class TestLzss(unittest.TestCase):
    
    def test_compress(self):
        expected = []
        for letter in 'Hello world! ':
            expected.append(Lzss.Token(True, ord(letter),0))
        expected.append(Lzss.Token(False, 12, 13))
        compressed = Lzss.Lzss().compress(b'Hello world! Hello world!', True)
        self.assertListEqual(expected, compressed)
    
    def test_no_repeating(self):
        expected = []
        data = []
        for i in range(0,255):
            data.append(i)
            expected.append(Lzss.Token(True, i, 0))
        compressed = Lzss.Lzss().compress(data, True)
        self.assertListEqual(expected, compressed)
