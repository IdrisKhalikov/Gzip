from ProgressBar import ProgressBar
from Crc32 import Crc32
import os.path
import Huffman
import Lzss_new


class Compresser:

    def compress_file(self, reader, writer, filename):
        lzss = Lzss_new.Lzss()
        crc = Crc32()
        total_length = 0
        filesize = os.path.getsize(filename)
        self._write_header(writer, filename)
        block = []
        self._progress_bar = ProgressBar(20, filesize)
        self._progress_bar.update()

        while bytes := reader.read(32768):
            block.extend(bytes)
            crc.add_bytes(bytes)
            total_length += len(bytes)
            compressed_data = list(lzss.compress(block))
            is_final = (total_length == filesize)
            self._write_block_01(writer, compressed_data, is_final)
            block = []
            self._progress_bar.set_value(total_length)
            self._progress_bar.update()
        writer.add_up()
        writer.write(crc.get_crc(), 32)
        writer.write(total_length % (2**32), 32)
        print(' '*56, end='\r')

    def _write_block_00(self, f, block_data, is_final):
        header = 1 if is_final else 0
        f.write(header, 1)  # flag if block is final
        f.write(0x00, 2)  # flag - block with no compression
        f.add_up()
        f.write(len(block_data), 16)
        f.write(~len(block_data), 16)
        for byte in block_data:
            f.write(byte)

    def _write_code_offset(self, f, code, offset):
        f.write(code.value, code.length, is_reversed=True)
        if offset.length > 0:
            f.write(offset.value, offset.length)

    def _write_block_01(self, f, compressed_data, is_final):
        f.write(1 if is_final else 0, 1)
        f.write(1, 2)
        huffman = Huffman.Fixed()
        for token in compressed_data:
            if token.is_literal:
                f.write(*huffman.get_literal(token.value), is_reversed=True)
                continue
            self._write_code_offset(f, *huffman.get_length(token.value))
            self._write_code_offset(f, *huffman.get_distance(token.offset))
        f.write(0x00,7)

    def _write_header(self, f, filename):
        f.write(0x1f)  # gzip id
        f.write(0x8b)  # gzip id
        f.write(0x08)  # using deflate compression
        f.write(0x08)  # flag - saving filename
        f.write(0x00, 32)  # mtime
        f.write(0x00)  # extra flags
        f.write(0x0b)  # os
        # writing filename
        bytes = str.encode(filename.rsplit('\\',1)[1])
        for byte in bytes:
            f.write(byte)
        f.write(0x00, 8)  # string end - null terminator
