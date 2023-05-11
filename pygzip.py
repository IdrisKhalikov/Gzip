from BitStream import BitStreamReader, BitStreamWriter
from Compresser import Compresser
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Compresses file using DEFLATE')
    parser.add_argument('filename', type=str, required=True)
    args = vars(parser.parse_args())
    compresser = Compresser()
    with BitStreamReader(args['filename']) as reader:
        name = args['filename'].rsplit('.')[0]
        with BitStreamWriter(f'{name}.gz') as writer:
            compresser.compress_file(reader, writer, args['filename'])
    print('OK')


if __name__ == '__main__':
    main()
