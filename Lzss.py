from typing import NamedTuple

LOOKAHEAD = 258  # max amount of characters to encode at once
BACKREF_LEN = 32768  # amount of characters we can backref to
MIN_LEN = 3  # minimal length of match to make backref

'''Each symbol/backref is saved in a tuple that contains
three values: a bool, that represents whether
the current segment is a symbol or a backref, and two ints,
which are: symbol code and 0, if the segment is a symbol, and
length and distance, if the segment is a backref'''
met = []


class Token(NamedTuple):
    is_literal: bool
    value: int
    offset: int = 0


def search_match(data, string):
    max_match_len = 0
    max_match_offset = 0
    cur_match = 0
    for index in range(len(data)):
        if cur_match < len(string) and data[index] == string[cur_match]:
            cur_match += 1
            if max_match_len <= cur_match:
                max_match_len = cur_match
                max_match_offset = len(data) - index + cur_match - 1
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


def compress(data):
    global met
    search_buffer = bytearray(data[:min(len(data), LOOKAHEAD)])
    index = len(search_buffer)

    while len(search_buffer) > 0:
        while len(met) > BACKREF_LEN:
            met = met[1:]
        match_len, offset = search_match(met, search_buffer)
        if match_len == -1:
            yield Token(True, search_buffer[0], 0)
            met.append(search_buffer.pop(0))
        else:
            token = Token(False, match_len, offset)
            met.extend(search_buffer[:match_len])
            search_buffer = search_buffer[match_len:]
            yield token
        while index < len(data) and len(search_buffer) < LOOKAHEAD:
            search_buffer.append(data[index])
            index += 1
        while len(search_buffer) > LOOKAHEAD:
            met.append(search_buffer.pop(0))
