from Crc32 import Crc32
import os.path


class Compresser:

    def compress_file(self, reader, writer, filename):
        crc = Crc32()
        total_length = 0
        name = os.path.splitext(filename)[0]
        self._write_header(writer, filename.split('/')[-1])
        block = []
        while not reader.is_eof():
            byte = reader.read(8)
            if len(block) == 65535 or reader.is_eof():
                self._write_block(writer, block, reader.is_eof())
            if not reader.is_eof():
                block.append(byte)
                crc.add(byte)
                total_length += 1

        writer.add_up()
        writer.write(crc.get_crc(), 32)
        writer.write(total_length % (2**32), 32)

    def _write_block(self, f, block_data, is_final):
        header = 1 if is_final else 0
        f.write(header, 1)  # flag if block is final
        f.write(0x00, 2)  # flag - block with no compression
        f.add_up()
        f.write(len(block_data), 16)
        f.write(~len(block_data), 16)
        for byte in block_data:
            f.write(byte)

    def _write_header(self, f, filename):
        f.write(0x1f)  # gzip id
        f.write(0x8b)  # gzip id
        f.write(0x08)  # using deflate compression
        f.write(0x08)  # flag - saving filename
        f.write(0x00, 32)  # mtime
        f.write(0x04)  # extra flags
        f.write(0x03)  # os
        # writing filename
        bytes = str.encode(filename, encoding='ascii')
        for byte in bytes:
            f.write(byte)
        f.write(0x00)  # string end - null terminator
