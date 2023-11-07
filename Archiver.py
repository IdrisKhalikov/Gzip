import os
import sys

'''ARCHIVE FORMAT:
1.filename/directory name
2.ZERO BYTE
3.ISFILE (0x00 if object is directory, 0xFF otherwise)
3.filesize, 12 byte field (if directory is encoded, this field can be filled with anything)
4.file content itself
5.ZERO BYTE'''

CHUNK_SIZE = 32768
END_OF_BLOCK = 0x00.to_bytes(1)

class Archiver:

    def create_archive(self, path_to):
        if os.path.isfile(path_to):
            yield from self._get_archived_file(path_to)
            return
        folders = [path_to]
        for cur_dir, subfolders, files in os.walk(path_to):
            cur_folder = self._get_name(cur_dir)
            while folders[-1] != cur_folder:
                folders.pop()
                yield END_OF_BLOCK
            folders.extend(reversed(subfolders))
            yield self._get_header(self._get_name(cur_dir), False)

            for file in files:
                yield from self._get_archived_file('\\'.join((cur_dir, file)))
        while folders:
            folders.pop()
            yield END_OF_BLOCK
    
    def _get_name(self, path):
        return path.rsplit('\\',1)[-1]
        
    def _get_header(self, name, is_file, filesize=0):
        header = bytearray()
        header.extend(str.encode(name, encoding='ascii'))
        header.extend(END_OF_BLOCK)
        header.append(0xFF if is_file else 0x00)
        header.extend(filesize.to_bytes(12))
        return header
    
    def _get_file_content(self, path):
        with open(path, 'rb') as reader:
            while bytes := reader.read(CHUNK_SIZE):
                yield bytes
    
    def _get_archived_file(self, path_to):
        filesize = os.path.getsize(path_to)
        yield self._get_header(self._get_name(path_to), True, filesize)
        yield from self._get_file_content(path_to)
        yield END_OF_BLOCK
    
class Dearchiver:
    def __init__(self):
        self._buffer = bytearray()

    def unarchive(self, byte_stream):
        self._stream = self._get_archive_reader(byte_stream)
        directory = os.getcwd()
        while True:
            name, isfile = self._try_write_file(directory)
            if not isfile:
                directory += f'\\{name}'
            while True:
                byte = next(self._stream, None)
                if byte is None:
                    return
                if byte == 0x00:
                    directory = directory.rsplit('\\',1)[0]
                else:
                    self._buffer.append(byte)
                    break

    def _is_eof(self):
        byte = next(self._stream)
        if byte is None:
            return True
        self._buffer.append(byte)
        return False

    def _get_archive_reader(self, byte_stream):
        while True:
            if self._buffer:
                yield self._buffer.pop()
            else:
                next_byte = next(byte_stream, None)
                if next_byte is None:
                    break
                yield next_byte
    
    def _read_until_end_of_block(self):
        data = bytearray()
        while (byte := next(self._stream)) != 0x00:
            data.append(byte)
        return data
    
    def _read_bytes(self, length):
        data = bytearray()
        for _ in range(length):
            data.append(next(self._stream))
        return data

    def _try_write_file(self, directory):
        name_bytes = self._read_until_end_of_block()
        name = name_bytes.decode(encoding='ascii')
        is_file = next(self._stream) == 0xFF
        filesize = int.from_bytes(self._read_bytes(12))
        path = '\\'.join((directory, name))
        if is_file:
            with open(path, 'wb') as f:
                f.write(self._read_bytes(filesize))
        else:
            os.mkdir(path)
        if is_file:
            next(self._stream)
        return name, is_file

def read_bytes(file):
    with open('test.archive', 'rb') as f:
        while byte := f.read(1):
            yield byte[0]
Dearchiver().unarchive(read_bytes('test'))