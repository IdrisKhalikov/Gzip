import os.path
import sys


class BitStreamWriter:

    def __init__(self, filename):
        self._buffer = 0
        self._buffer_length = 0
        self._file = filename

    def write(self, value, bit_length=8, is_reversed=False):
        mask = (1 << bit_length) - 1
        value = value & mask
        if is_reversed:
            value = self._reverse(value, bit_length)
        self._buffer |= (value << self._buffer_length)
        self._buffer_length += bit_length
        while (self._write_stream()):
            pass

    def _write_stream(self):
        if self._buffer_length < 8:
            return False
        byte = (self._buffer & 0xFF).to_bytes(1)
        self._stream.write(byte)
        self._buffer_length -= 8
        self._buffer >>= 8
        return True

    def _reverse(self, value, length):
        reversed = 0
        for i in range(length):
            reversed <<= 1
            reversed |= ((value >> i) & 1)
        return reversed

    def add_up(self):
        if self._buffer_length > 0:
            self.write(0, 8-self._buffer_length)

    def __enter__(self):
        self._stream = open(self._file, 'wb')
        return self

    def __exit__(self, exception, value, traceback):
        self.add_up()
        self._stream.close()


class BitStreamReader:

    def __init__(self, filename):
        self._buffer = 0
        self._buffer_length = 0
        self._eof = False
        self._file = self._get_path(filename)

    def _get_path(self, filename):
        for path in sys.path:
            for root, dirs, files in os.walk(path):
                if filename in files:
                    return os.path.join(root, filename)
        raise FileNotFoundError(f'File {filename} was not found!')

    def read(self, bit_length=8, is_reversed=False):
        if self._buffer_length < bit_length and self._eof == False:
            self._read_stream(bit_length)
        mask = (1 << bit_length) - 1
        value = self._buffer & mask
        self._buffer >>= bit_length
        self._buffer_length -= bit_length
        if is_reversed:
            return self._reverse(value, bit_length)
        return value

    def is_eof(self):
        return self._eof or self._buffer_length < 0

    def _read_stream(self, bit_length=8):
        add_bytes_len = ((bit_length // 8) + 1)
        bytes = self._stream.read(add_bytes_len)
        value = 0
        length = 0
        if len(bytes) != add_bytes_len:
            self._eof = True
        for i in range(len(bytes)):
            value |= (bytes[i] << length)
            length += 8
        if length != 0:
            self._buffer |= (value << self._buffer_length)
            self._buffer_length += length

    def _reverse(value, length):
        reversed = 0
        for i in range(length):
            reversed <= 1
            reversed |= (value >> i)
        return reversed

    def __enter__(self):
        self._stream = open(self._file, 'rb')
        return self

    def __exit__(self, exception, value, traceback):
        self._stream.close()
