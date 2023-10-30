from typing import NamedTuple
from BinarySearchTree import BST

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

class Lzss:
    def __init__(self):
        self._buffer = [-1]*(BACKREF_LEN + LOOKAHEAD - 1)  # Циклический буфер
        self._nodes = [None]*BACKREF_LEN
        self._trees = [BST(self._buffer, LOOKAHEAD) for _ in range(256)]
        self._last_match = 1
        self._left = 0
        self._right = LOOKAHEAD
        self._was_init = False

    def _delete_last_node(self):
        if self._buffer[self._right] == -1:
            return
        self._trees[self._buffer[self._right]].delete(self._nodes[self._right])
        self._nodes[self._right] = None

    def _insert_next_node(self):
        if self._buffer[self._left] == -1:
            return (0,0)
        match_len, index, node = self._trees[self._buffer[self._left]].insert(self._left)
        self._nodes[self._left] = node
        return match_len, index
    
    def _move_symbol(self, byte=None):
        self._delete_last_node()
        if byte is not None:
            self._set_symbol(self._right, byte)
        self._right = (self._right + 1) % BACKREF_LEN
        match = self._insert_next_node()
        self._left = (self._left + 1) % BACKREF_LEN
        return match
    
    def _set_symbol(self, index, value):
        self._buffer[index] = value
        if index < LOOKAHEAD - 1:
            self._buffer[index + BACKREF_LEN] = value

    def _init_buffer(self, data):
        init_length = min(LOOKAHEAD, len(data))
        for i in range(init_length):
            next_pos = (self._left + i) % BACKREF_LEN
            self._set_symbol(next_pos, data[i])
        self._was_init = True
        return i + 1

    def compress(self, data, is_final):
        index = 0
        is_first_run = not self._was_init
        if not self._was_init:
            index = self._init_buffer(data)

        to_process = len(data)
        if is_first_run:
            to_process -= LOOKAHEAD
        if is_final:
            to_process += LOOKAHEAD

        while to_process > 0:
            last_symbol = self._buffer[self._left]
            last_index = self._left
            byte = data[index] if index < len(data) else None
            match_len, match_index = self._move_symbol(byte)
            if match_len > to_process:
                match_len = to_process
            to_process -= 1
            index += 1

            if match_len < MIN_LEN:
                match_len = 1
                yield Token(True, last_symbol, 0)
            else:
                if last_index < match_index:
                    last_index += BACKREF_LEN
                offset = last_index - match_index
                for _ in range(match_len - 1):
                    byte = data[index] if index < len(data) else None
                    self._move_symbol(byte)
                    to_process -= 1
                    index += 1
                yield Token(False, match_len, offset)
