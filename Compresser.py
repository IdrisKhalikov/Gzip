from Crc32 import Crc32
import os.path
import Huffman
import Lzss


class Compresser:

    def compress_file(self, reader, writer, filename):
        crc = Crc32()
        total_length = 0
        filesize = os.path.getsize(filename)
        self._write_header(writer, filename)
        block = []
        self._print_progress(0, filesize)

        while bytes := reader.read(32768):
            block.extend(bytes)
            crc.add(bytes)
            total_length += len(bytes)
            self._write_block_01(writer, block, total_length == filesize)
            block = []
            self._print_progress(total_length, filesize)
        writer.add_up()
        writer.write(crc.get_crc(), 32)
        writer.write(total_length % (2**32), 32)
        print(' '*56, end='\r')

    def _print_progress(self, processed, filesize):
        progress = round((processed / filesize)*100, 2)
        progress_bar = ((int(progress//5))*'▇').ljust(20, '-')
        print(f'Progress:[{progress_bar}] {progress}%', end='\r')

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

    def _write_block_01(self, f, block_data, is_final):
        f.write(1 if is_final else 0, 1)
        f.write(1, 2)
        compressed = Lzss.compress(block_data)
        huffman = Huffman.Fixed()
        for token in compressed:
            if token.is_literal:
                f.write(*huffman.get_literal(token.value), is_reversed=True)
                continue
            self._write_code_offset(f, *huffman.get_length(token.value))
            self._write_code_offset(f, *huffman.get_distance(token.offset))
        f.write(0x00, 7)

    def _write_block_02(self, f, block_data, is_final):
        f.write(1 if is_final else 0, 1)
        f.write(2, 2)

        compressed = list(Lzss.compress(block_data))
        compressed.append(Lzss.Token(True, 256, 0))
        huffman = Huffman.Fixed()
        length_alphabet = []
        offset_alphabet = []
        for token in compressed:
            if token.is_literal:
                length_alphabet.append(token.value)
                continue
            length, _ = huffman.get_length_code(token.value)
            length_alphabet.append(length)
            offset, _ = huffman.get_distance_code(token.offset)
            offset_alphabet.append(offset)

        length_codes, _ = Huffman.compress(length_alphabet)
        offset_codes, _ = Huffman.compress(offset_alphabet)
        # cl stands for 'code lengths'
        length_cl = self.get_full_codes(length_codes, 286)
        offset_cl = self.get_full_codes(offset_codes, 32)
        hlit = len(length_cl) - 257
        hdist = len(offset_cl) - 1

        length_cl, l_add_codes = self.skip_repeat_codes(length_cl)
        offset_cl, dist_add_codes = self.skip_repeat_codes(offset_cl)
        cl_codes = length_cl + offset_cl
        cl_add_codes = l_add_codes + dist_add_codes
        cl_code_coded, _ = Huffman.compress([code.length for code in cl_codes])
        order = [16, 17, 18, 0, 8, 7, 9, 6, 10,
                 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
        cl_code_code = []
        last_index = 0
        for i in range(len(order)):
            if order[i] in cl_code_coded:
                cl_code_code.append(cl_code_coded[order[i]])
                last_index = i
            else:
                cl_code_code.append(Huffman.Code(0, 3))
        cl_code_code = cl_code_code[:last_index+1]
        hclen = len(cl_code_code) - 4

        f.write(hlit, 5)
        f.write(hdist, 5)
        f.write(hclen, 4)
        for code in cl_code_code:
            f.write(code.length, 3, is_reversed=True)
        add_code_index = 0
        for code in cl_codes:
            coded = cl_code_coded[code.length]
            f.write(coded.value, coded.length, is_reversed=True)
            if code.length >= 16:
                add_bits = cl_add_codes[add_code_index]
                f.write(add_bits.value, add_bits.length)
                add_code_index += 1
        for token in compressed:
            if token.is_literal:
                code = length_codes[token.value]
                f.write(code.value, code.length, is_reversed=True)
                continue

            index, offset = huffman.get_length_code(token.value)
            len_code = length_codes[index]
            f.write(len_code.value, len_code.length, is_reversed=True)
            if offset.length > 0:
                f.write(offset.value, offset.length)
            index, offset = huffman.get_distance_code(token.offset)
            dist_code = offset_codes[index]
            f.write(dist_code.value, dist_code.length, is_reversed=True)
            if offset.length > 0:
                f.write(offset.value, offset.length)

    def get_full_codes(self, codes, max_length):
        all_codes = []
        last_index = 0
        for i in range(max_length):
            if i not in codes:
                all_codes.append(Huffman.Code(0, 0))
                continue
            all_codes.append(codes[i])
            last_index = i
        all_codes = all_codes[:last_index+1]
        return all_codes

    # Протестировать все
    def skip_repeat_codes(self, codes):
        skipped = []
        extra_bits = []
        cur_repeat = Huffman.Code(-1, -1)
        cur_count = 0
        for code in codes:
            if code.value == cur_repeat.value:
                cur_count += 1
                continue
            if cur_count < 3:
                if cur_count != 0:
                    skipped.extend([skipped[-1]]*cur_count)
            else:
                shortened, add_codes = self.remove_repeat(
                    cur_count, cur_repeat)
                skipped.extend(shortened)
                extra_bits.extend(add_codes)
            cur_count = 0
            skipped.append(code)
            cur_repeat = code
        return (skipped, extra_bits)

    def remove_repeat(self, count, code):
        remove_list = []
        max_remove = 138 if code.value == 0 else 6
        while True:
            for i in range(max_remove, 2, -1):
                if count - i >= 0:
                    count -= i
                    remove_list.append(i)
                    continue
            break
        result = []
        add_codes = []
        result.extend([code]*count)
        for val in remove_list:
            if code.value == 0:
                if val > 10:
                    result.append(Huffman.Code(0, 18))
                    add_codes.append(Huffman.Code(val-11, 7))
                else:
                    result.append(Huffman.Code(0, 17))
                    add_codes.append(Huffman.Code(val-3, 3))
            else:
                result.append(Huffman.Code(0, 16))
                add_codes.append(Huffman.Code(val-3, 3))
        return (result, add_codes)

    def _write_header(self, f, filename):
        f.write(0x1f)  # gzip id
        f.write(0x8b)  # gzip id
        f.write(0x08)  # using deflate compression
        f.write(0x08)  # flag - saving filename
        f.write(0x00, 32)  # mtime
        f.write(0x00)  # extra flags
        f.write(0x0b)  # os
        # writing filename
        bytes = str.encode(filename, encoding='ascii')
        for byte in bytes:
            f.write(byte)
        f.write(0x00, 8)  # string end - null terminator
