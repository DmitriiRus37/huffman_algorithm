import os
import sys

import compression
import decompression


def main():
    if sys.argv[1] == 'decode':
        dec = decompression.Algorythm()
        source_path = os.path.abspath(sys.argv[2])
        dest_path = os.path.abspath(sys.argv[3])
        dec.decompress(source_path, dest_path)
    else:
        c = compression.Algorythm()
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        c.compress(source_path, dest_path)


if __name__ == "__main__":
    main()
