import unittest
import Huffman

class TestHuffman(unittest.TestCase):
    
    def test_compress_single(self):
        text = 'A'
        self.assertDictEqual(Huffman.compress(text), {'A':Huffman.Code(0,1)})
    
    def test_compress_multiple(self):
        text = 'ABC'
        expected = {
            'A':Huffman.Code(2,2),
            'B':Huffman.Code(3,2),
            'C':Huffman.Code(0,1)
        }
        self.assertDictEqual(Huffman.compress(text), expected)

    def test_compress_different_frequencies(self):
        text = 'AAABBC'
        expected = {
            'A':Huffman.Code(0,1),
            'B':Huffman.Code(2,2),
            'C':Huffman.Code(3,2)
        }
        self.assertDictEqual(Huffman.compress(text), expected)

    def test_from_code_lengths(self):
        code_lengths = [
            ('A',3),
            ('B',3),
            ('C',3),
            ('D',3),
            ('E',3),
            ('F',2),
            ('G',4),
            ('H',4)
        ]

        expected = {
            '010': 'A',
            '011': 'B',
            '100': 'F',
            '101': 'D',
            '110': 'E',
            '10010': 'G',
            '10011': 'H'
        }

        self.assertDictEqual(Huffman.get_from_code_lengths(code_lengths), expected)

    def test_find_closest(self):
        values = [(1,0),(3,1),(5,1)]
        huffman = Huffman.Fixed()
        self.assertEqual(huffman._find_closest(values,1),0)
        self.assertEqual(huffman._find_closest(values,2),0)
        self.assertEqual(huffman._find_closest(values,3),1)
        self.assertEqual(huffman._find_closest(values,6),2)

    def test_get_index_offset(self):
        values = [(1,1),(3,1),(5,3)]
        huffman = Huffman.Fixed()
        self.assertEqual(huffman._get_index_offset(values,1),(0, Huffman.Code(0,1)))
        self.assertEqual(huffman._get_index_offset(values,2),(0, Huffman.Code(1,1)))
        self.assertEqual(huffman._get_index_offset(values,3),(1, Huffman.Code(0,1)))
        self.assertEqual(huffman._get_index_offset(values,6),(2, Huffman.Code(1,3)))
        