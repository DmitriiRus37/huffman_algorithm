import os
import sys

import compression
import decompression


def main():

    if sys.argv[1] == 'decode':
        dec = decompression.Algorythm()
        source_path = os.path.abspath(sys.argv[2])
        dest_path = os.path.abspath(sys.argv[3])
        dec.get_table_of_codes(source_path)
        dec.decode(source_path, dest_path)
    else:
        c = compression.Algorythm()
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        c.compress(source_path, dest_path)


main()
