import os.path
import sys

class BitStreamWriter:

    def __init__(self, filename, buffer_size=32768):
        self._buffer = bytearray()
        self._last_byte = 0
        self._byte_len = 0
        self._buffer_size = buffer_size
        self._file = filename

    def write(self, value, bit_length=8, is_reversed=False):
        mask = (1 << bit_length) - 1
        value = value & mask
        if is_reversed:
            value = self._reverse(value, bit_length)
        self._last_byte |= (value << self._byte_len)
        self._byte_len += bit_length
        while self._byte_len >= 8:
            self._buffer.append(self._last_byte & 0xFF)
            self._last_byte >>= 8
            self._byte_len -= 8

        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def _reverse(self, value, length):
        reversed = 0
        for i in range(length):
            reversed <<= 1
            reversed |= ((value >> i) & 1)
        return reversed

    def add_up(self):
        if self._byte_len > 0:
            self.write(0x00, 8-self._byte_len)
    
    def flush(self):
        self._stream.write(self._buffer)
        self._buffer.clear()

    def __enter__(self):
        self._stream = open(self._file, 'wb')
        return self

    def __exit__(self, exception, value, traceback):
        self.add_up()
        self.flush()
        self._stream.close()


class BitStreamReader:

    def __init__(self, filename):
        self._buffer = BitArray()
        self._eof = False
        self._file = self._get_path(filename)

    def _get_path(self, filename):
        for root, dirs, files in os.walk(os.getcwd()):
            if filename in files:
                return os.path.join(root, filename)
        sys.exit(f'File {filename} was not found!')

    def read(self, bit_length=8, is_reversed=False):
        if len(self._buffer) < bit_length and self._bytes_left > 0:
            self._read_stream((bit_length - len(self._buffer)) // 8 + 1)
        value = self._buffer.pop(bit_length)
        if is_reversed:
            return self._reverse(value, bit_length)
        return value

    def read_assert(self, expected, bit_length=8, is_reversed=False):
        value = self.read(bit_length, is_reversed)
        if value != expected:
            raise AssertionError(
                f'Expected to read: {hex(expected)}, but was: {hex(value)}')

    def is_eof(self):
        return self._bytes_left == 0 and len(self._buffer) <= 0

    def _read_stream(self, byte_len):
        bytes = self._stream.read(byte_len)
        self._bytes_left -= len(bytes)
        self._buffer.extend(bytes)

    def _reverse(self, value, length):
        reversed = 0
        for i in range(length):
            reversed <<= 1
            reversed |= (value >> i) & 1
        return reversed & ((1 << length) - 1)
    
    def skip_to_byte_boundary(self):
        to_skip = len(self._buffer) - (len(self._buffer) // 8) * 8
        if to_skip > 0:
            self._buffer.pop(to_skip)

    def get_path(self):
        return self._stream.name

    def __enter__(self):
        self._stream = open(self._file, 'rb')
        self._bytes_left = os.path.getsize(self._file)
        return self

    def __exit__(self, exception, value, traceback):
        self._stream.close()


class BitArray:

    def __init__(self):
        self._buffer = 0
        self._buffer_len = 0

    def append(self, value, bit_length=8):
        mask = (1 << bit_length) - 1
        value = value & mask
        self._buffer |= (value << self._buffer_len)
        self._buffer_len += bit_length

    def extend(self, data):
        for byte in data:
            self.append(byte)

    def pop(self, bit_length=8):
        mask = (1 << bit_length) - 1
        value = self._buffer & mask
        self._buffer >>= min(self._buffer_len, bit_length)
        self._buffer_len -= min(self._buffer_len, bit_length)
        return value

    def __len__(self):
        return self._buffer_len
