from heapq import heappush, heappop
from collections import Counter
from typing import NamedTuple


class Code(NamedTuple):
    value: int
    length: int


class Fixed:

    LENGTHS = [(3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 1), (13, 1), (15, 1), (17, 1), (19, 2), (23, 2), (27, 2),
               (31, 2), (35, 3), (43, 3), (51, 3), (59, 3), (67, 4), (83, 4), (99, 4), (115, 4), (131, 5), (163, 5), (195, 5), (227, 5), (258, 0)]
    DISTANCES = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 1), (7, 1), (9, 2), (13, 2), (17, 3), (25, 3), (33, 4), (49, 4), (65, 5), (97, 5), (129, 6), (193, 6), (257, 7),
                 (385, 7), (513, 8), (769, 8), (1025, 9), (1537, 9), (2049, 10), (3073, 10), (4097, 11), (6145, 11), (8193, 12), (12289, 12), (16385, 13), (24577, 13)]
    CODES = [(0, 0x30, 8), (144, 0x190, 9), (256, 0x00, 7), (280, 0xC0, 8)]

    def _find_closest(self, values, value):
        for i in range(len(values)):
            if values[i][0] > value:
                return i - 1
        return i

    def _get_code(self, value):
        index = self._find_closest(self.CODES, value)
        coded = self.CODES[index][1] + (value - self.CODES[index][0])
        return Code(coded, self.CODES[index][2])

    def get_literal(self, value):
        assert (0 <= value <= 255)
        return self._get_code(value)

    def _get_index_offset(self, table, value):
        index = self._find_closest(table, value)
        offset = value - table[index][0]
        return (index, Code(offset, table[index][1]))

    def get_length(self, value):
        index, offset = self._get_index_offset(self.LENGTHS, value)
        index += 257
        return (self._get_code(index), offset)

    def get_distance(self, value):
        index, offset = self._get_index_offset(self.DISTANCES, value)
        return (Code(index, 5), offset)
    
    def get_length_code(self, value):
        index, offset = self._get_index_offset(self.LENGTHS, value)
        index += 257
        return (index, offset)
    
    def get_distance_code(self, value):
        index, offset = self._get_index_offset(self.DISTANCES, value)
        return (index, offset)

def get_huffman(bytes):
    frequencies = Counter(bytes)
    tree = []
    codes = {byte: '' for byte in bytes}
    for value, count in frequencies.items():
        heappush(tree, (count, [value]))

    while len(tree) > 1:
        left_node = heappop(tree)
        right_node = heappop(tree)

        for value in left_node[1]:
            codes[value] = '0' + codes[value]
        for value in right_node[1]:
            codes[value] = '1' + codes[value]

        heappush(tree, (left_node[0]+right_node[0],
                 sorted(left_node[1] + right_node[1])))

    sorted_codes = sorted(codes.items(), key=lambda t: (t[1], t[0]))
    code = 0
    cur_length = 1
    code_lengths = {}
    for code_pair in sorted_codes:
        while len(code_pair[1]) > cur_length:
            cur_length += 1
            code <<= 1
        codes[code_pair[0]] = code
        code_lengths[code_pair[0]] = Code(code, cur_length)
        code += 1
    return code_lengths


def compress(data):
    codes = get_huffman(data)
    encoded = ''.join(bin(codes[value].value)[2:].zfill(codes[value].length) for value in data)
    return codes, encoded
