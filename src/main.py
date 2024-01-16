import os
import sys

from compression import Compression
from decompression import Decompression
from helpers import get_compression_info


# TODO add compressing of some files to one compressed_file
def main():
    if sys.argv[1] == 'decode':
        source_path = os.path.abspath(sys.argv[2])
        dest_path = os.path.abspath(sys.argv[3])
        d = Decompression()
        d.decompress(source_path, dest_path)
        get_compression_info(dest_path, source_path)
    else:
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        c = Compression()
        c.compress(source_path, dest_path)
        get_compression_info(source_path, dest_path)


if __name__ == "__main__":
    main()
