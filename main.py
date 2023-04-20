import os
import sys

from compression import Compression
from decompression import Decompression


def main():
    if sys.argv[1] == 'decode':
        source_path = os.path.abspath(sys.argv[2])
        dest_path = os.path.abspath(sys.argv[3])
        dec = Decompression()
        dec.decompress(source_path, dest_path)
    else:
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        c = Compression()
        c.compress(source_path, dest_path)


if __name__ == "__main__":
    main()
