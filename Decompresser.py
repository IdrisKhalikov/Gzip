from BitStream import BitStreamReader
from Crc32 import Crc32
import Huffman
from SlidingWindow import SlidingWindow
import sys


class Decompresser:

    def __init__(self):
        self._default_codes = self._get_default_codes()

    def decompress(self, reader):
        crc32 = Crc32()
        total_length = 0
        filename = self._read_header(reader)
        if not filename:
            filename = reader.get_path()
        if filename.endswith('.gz'):
            filename = filename[:-3]
        writer = open(filename, 'wb')
        buffer = SlidingWindow(32768)
        is_final = False
        while not is_final:
            is_final = True if reader.read(1) == 1 else False
            block_type = reader.read(2)
            if block_type == 0x00:
                total_length += self._read_block_00(reader, writer, crc32)
            if block_type == 0x01:
                total_length += self._read_block_01(reader, writer, buffer, crc32)
        writer.close()
        reader.skip_to_byte_boundary()
        crc_code = reader.read(32)
        if crc32.get_crc() != crc_code:
            sys.exit('Crc codes do not match!')
        actual_len = reader.read(32)
        if total_length % 2**32 != actual_len:
            sys.exit('Data lengths do not match!')
        return filename

    def _read_block_00(self, reader, writer, crc):
        reader.read(5)
        length = reader.read(16)
        neg_len = reader.read(16)
        assert length == (~neg_len & 0xFFFF)
        for _ in range(length):
            byte = reader.read()
            crc.add(byte)
            writer.write(byte.to_bytes())
        return length

    def _read_block_01(self, reader, writer, buffer, crc):
        length = 0
        fixed_codes = Huffman.Fixed()
        codes = self._default_codes
        while (code := self._read_next_code(reader, codes)) is not None:
            if code < 256:
                buffer.add(code)
                crc.add(code)
                writer.write(code.to_bytes())
                length += 1
                continue
            backref_len, add_len = fixed_codes.LENGTHS[code-257]
            if add_len > 0:
                add = reader.read(add_len)
                backref_len += add
            dist_code = reader.read(5, is_reversed=True)
            dist, add_dist = fixed_codes.DISTANCES[dist_code]
            if add_dist > 0:
                dist += reader.read(add_dist)
            for _ in range(backref_len):
                buffer.add(buffer.get_last(dist-1))
                crc.add(buffer.get_last())
                writer.write(buffer.get_last().to_bytes())
                length += 1
        return length

    def _read_next_code(self, reader, codes):
        code = ''
        while True:
            code += ('1' if reader.read(1) == 1 else '0')
            if code not in codes:
                continue
            value = codes[code]
            if value == 256:
                return None
            return value

    def _get_default_codes(self):
        code_lengths = []
        for i in range(256, 280):
            code_lengths.append((i, 7))
        for i in range(144):
            code_lengths.append((i, 8))
        for i in range(280, 288):
            code_lengths.append((i, 8))
        for i in range(144, 256):
            code_lengths.append((i, 9))
        return Huffman.get_from_code_lengths(code_lengths)
        

    def _read_header(self, f):
        f.read_assert(0x1f)  # gzip id
        f.read_assert(0x8b)  # gzip id
        f.read_assert(0x08)  # using deflate compression
        is_name_saved = (f.read() == 0x08)  # flag - saving filename
        f.read(32)  # mtime
        f.read(8)  # extra flags
        f.read(8)  # os
        # writing filename
        if not is_name_saved:
            return None
        bytes = bytearray()
        while True:
            byte = f.read(8)
            if byte == 0x00:
                break
            bytes.append(byte)
        return bytes.decode()
