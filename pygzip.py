from BitStream import BitStreamReader, BitStreamWriter
from Decompresser import Decompresser
from Compresser import Compresser
import argparse
import sys
import os


def get_path(filename):
    for root, dirs, files in os.walk(os.getcwd()):
        if filename in files:
            return os.path.join(root, filename)
    sys.exit(f'File {filename} was not found!')

def main(*args, **kwargs):
    args = get_args()
    if args['c']:
        compress(args['c'])
    if args['d']:
        decompress(args['d'])
    print('OK')
    sys.exit(0)

def get_args():
    parser = argparse.ArgumentParser(
    description='Compresses file using DEFLATE')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', type=str)
    group.add_argument('-d', type=str)
    args = vars(parser.parse_args())
    return args

def compress(filename):
    with open(get_path(filename), 'rb') as reader:
            name = reader.name.rsplit('\\',1)[1]
            with BitStreamWriter(f'{name}.gz') as writer:
                Compresser().compress_file(reader, writer, reader.name)

def decompress(filename):
    with BitStreamReader(filename) as reader:
        Decompresser().decompress(reader)

if __name__ == '__main__':
    main()
