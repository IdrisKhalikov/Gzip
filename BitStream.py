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
            self.write(0x00, 8-self._buffer_length)

    def __enter__(self):
        self._stream = open(self._file, 'wb')
        return self

    def __exit__(self, exception, value, traceback):
        self.add_up()
        self._stream.close()


class BitStreamReader:

    def __init__(self, filename):
        self._buffer = bytearray()
        self._cur_byte_len = 0
        self._eof = False
        self._file = self._get_path(filename)

    def _get_path(self, filename):
        for root, dirs, files in os.walk(os.getcwd()):
            if filename in files:
                return os.path.join(root, filename)
        sys.exit(f'File {filename} was not found!')

    def read_bits(self, bit_length=8, is_reversed=False):
        if self._buffer_length < bit_length and self._bytes_left > 0:
            self._read_stream((bit_length - self._buffer_length) //8 + 1)
        mask = (1 << bit_length) - 1
        value = self._buffer & mask
        self._buffer >>= bit_length
        self._buffer_length -= bit_length
        if is_reversed:
            return self._reverse(value, bit_length)
        return value

    def is_eof(self):
        return self._bytes_left == 0 and self._buffer_length <= 0

    def _read_stream(self, byte_len):
        bytes = self._stream.read(byte_len)
        self._bytes_left -= len(bytes)
        self._buffer.append(bytes)

    def _reverse(value, length):
        reversed = 0
        for i in range(length):
            reversed <<= 1
            reversed |= (value >> i)
        return reversed
    
    def get_path(self):
        return self._stream.name

    def __enter__(self):
        self._stream = open(self._file, 'rb')
        self._bytes_left = os.path.getsize(self._file)
        return self

    def __exit__(self, exception, value, traceback):
        self._stream.close()
