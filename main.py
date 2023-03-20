import os
import sys

import argparse
import compression


def main():
    debug_info = True if '-d' in sys.argv or '--debug' in sys.argv else False

    if sys.argv[1] == 'str':
        print(compression.compress_str(str(sys.argv[2]), debug_info))
    else:
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        compression.compress_file(source_path, dest_path)


main()