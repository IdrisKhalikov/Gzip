from BitStream import BitStreamReader, BitStreamWriter
from Compresser import Compresser
import argparse
import sys
import os


def get_path(filename):
    for root, dirs, files in os.walk(os.getcwd()):
        if filename in files:
            return os.path.join(root, filename)
    sys.exit(f'File {filename} was not found!')

def main(args=None):
    parser = argparse.ArgumentParser(
        description='Compresses file using DEFLATE')
    parser.add_argument('filename', type=str)
    args = vars(parser.parse_args())
    compresser = Compresser()
    with open(get_path(args['filename']), 'rb') as reader:
        name = reader.name.rsplit('.',1)[0]
        with BitStreamWriter(f'{name}.gz') as writer:
            compresser.compress_file(reader, writer, reader.name)
    print('OK')
    sys.exit(0)


if __name__ == '__main__':
    main()
