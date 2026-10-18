import argparse
import os
import sys

from huffman import Compression, Decompression, HuffmanError, get_compression_info

COMMANDS = ('compress', 'decompress', 'decode')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Compress and decompress files with the Huffman algorithm.',
        epilog='For backward compatibility "main.py SOURCE DEST" compresses '
               'and "main.py decode SOURCE DEST" decompresses.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    for name, aliases, help_text in (('compress', [], 'compress SOURCE into DEST'),
                                     ('decompress', ['decode'], 'decompress SOURCE into DEST')):
        sub = subparsers.add_parser(name, aliases=aliases, help=help_text)
        sub.add_argument('source', help='input file')
        sub.add_argument('dest', help='output file')
        sub.add_argument('-q', '--quiet', action='store_true', help='no progress bars and timings')
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] not in COMMANDS and not argv[0].startswith('-'):
        argv = ['compress', *argv]
    args = build_parser().parse_args(argv)
    source_path = os.path.abspath(args.source)
    dest_path = os.path.abspath(args.dest)
    verbose = not args.quiet
    try:
        if args.command == 'compress':
            Compression(verbose=verbose).compress(source_path, dest_path)
            if verbose:
                get_compression_info(source_path, dest_path)
        else:
            Decompression(verbose=verbose).decompress(source_path, dest_path)
            if verbose:
                get_compression_info(dest_path, source_path)
    except (HuffmanError, OSError) as e:
        print(f'error: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
