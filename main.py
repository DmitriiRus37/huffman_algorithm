import os
import sys

import algorythm



def main():
    alg = algorythm.Algorythm()

    debug_info = True if '-d' in sys.argv or '--debug' in sys.argv else False

    if sys.argv[1] == 'str':
        decoded_str = alg.compress_str(str(sys.argv[2]), debug_info)
        print(decoded_str)
    else:
        source_path = os.path.abspath(sys.argv[1])
        dest_path = os.path.abspath(sys.argv[2])
        alg.compress_file(source_path, dest_path)


main()