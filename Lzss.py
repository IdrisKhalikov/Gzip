from typing import NamedTuple

LOOKAHEAD = 258  # Размер буфера из незакодированных символов.
BACKREF_LEN = 32768  # Размер словаря
MIN_LEN = 3  # Минимальная длина кодируемого сообщения

'''Each symbol/backref is saved in a tuple that contains
three values: a bool, that represents whether
the current segment is a symbol or a backref, and two ints,
which are: symbol code and 0, if the segment is a symbol, and
length and distance, if the segment is a backref'''
class Token(NamedTuple):
    is_literal: bool
    value: int
    offset: int = 0

class SlidingWindow:
    def __init__(self, length):
        self._length = length
        self._buffer = []

    def append(self, value):
        self._buffer.append(value)
        self._reduce()

    def _reduce(self):
        if len(self._buffer) > self._length:
            self._buffer = self._buffer[len(self._buffer)-self._length:]

    def __getitem__(self, index):
        return self._buffer[index]
    
    def extend(self, values):
        self._buffer.extend(values)
        self._reduce()
    
    def __len__(self):
        return len(self._buffer)


class Lzss:
    def __init__(self):
        self._met = SlidingWindow(BACKREF_LEN)

    def _search_match(self, string):
        max_match_len = 0
        max_match_offset = 0
        cur_match = 0
        for index in range(len(self._met)):
            if cur_match < len(string) and self._met[index] == string[cur_match]:
                cur_match += 1
                if max_match_len <= cur_match:
                    max_match_len = cur_match
                    max_match_offset = len(self._met) - index + cur_match - 1
            else:
                # Откатываемся назад, на случай если считанный символ совпадает с началом строки
                index -= cur_match
                cur_match = 0
        if max_match_len < MIN_LEN:
            return (-1, -1)
        token_len = max_match_len.bit_length() + max_match_offset.bit_length()
        if token_len > len(string) * 8:
            return (-1, -1)
        return (max_match_len, max_match_offset)


    def compress(self,data):
        search_buffer = bytearray(data[:min(len(data), LOOKAHEAD)])
        index = len(search_buffer)

        while len(search_buffer) > 0:
            match_len, offset = self._search_match(search_buffer)
            if match_len == -1:
                yield Token(True, search_buffer[0], 0)
                self._met.append(search_buffer.pop(0))
            else:
                token = Token(False, match_len, offset)
                self._met.extend(search_buffer[:match_len])
                search_buffer = search_buffer[match_len:]
                yield token
            while index < len(data) and len(search_buffer) < LOOKAHEAD:
                search_buffer.append(data[index])
                index += 1
            while len(search_buffer) > LOOKAHEAD:
                self._met.append(search_buffer.pop(0))
