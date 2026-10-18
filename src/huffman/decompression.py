import os
import zlib
from itertools import islice
from bitarray import bitarray, decodetree
from .compression import MAGIC, FORMAT_VERSION, PARTITION_SIZE
from .helpers import print_time_spent, update_pbar
from tqdm import tqdm


class Decompression:
    def __init__(self):
        self.table_of_codes = {}
        self.symbols_count = 0
        self.crc = 0

    @print_time_spent(message="to read all bytes from file")
    def read_from_file(self, f) -> int:
        tree, header_bytes = self.read_header(f)
        if len(tree) == 2:
            # a single symbol in the source file gets code '0'
            self.restore_tree(tree, 0, '0')
        elif tree:
            if self.restore_tree(tree, 0, '') != len(tree):
                raise Exception('header is invalid')
        return header_bytes

    @print_time_spent(message="to decompress")
    def decompress(self, source: str, dest: str) -> None:
        with open(source, "rb") as f_in, open(dest, "wb") as f_out:
            header_bytes = self.read_from_file(f_in)
            pbar = tqdm(total=float(os.path.getsize(source) / 1024 / 1024),
                        unit="Mb", unit_scale=True,
                        desc="Decoded")
            update_pbar(header_bytes / 1024 / 1024, pbar)
            crc = self.decode_data(f_in, f_out, pbar)
            pbar.close()
        if crc != self.crc:
            raise Exception('encoded file invalid: CRC32 mismatch')

    def decode_data(self, f_in, f_out, pbar: tqdm) -> int:
        if not self.table_of_codes:
            if self.symbols_count or f_in.read(1):
                raise Exception('encoded file invalid!!!')
            return 0
        code_dict = {symbol: bitarray(code) for code, symbol in self.table_of_codes.items()}
        tree = decodetree(code_dict)
        remaining = self.symbols_count
        rest_bits = bitarray()
        crc = 0
        while remaining:
            partition = f_in.read(PARTITION_SIZE)
            if not partition:
                raise Exception('encoded file is truncated')
            update_pbar(len(partition) / 1024 / 1024, pbar)
            rest_bits.frombytes(partition)
            symbols = []
            try:
                # stop at `remaining` so the zero padding at the end is never decoded
                symbols.extend(islice(rest_bits.decode(tree), remaining))
            except ValueError:
                # the block ends inside a code; list.extend() keeps the symbols decoded before it
                pass
            consumed = bitarray()
            consumed.encode(code_dict, symbols)
            del rest_bits[:len(consumed)]
            data = bytes(symbols)
            crc = zlib.crc32(data, crc)
            f_out.write(data)
            remaining -= len(symbols)
        if len(rest_bits) >= 8 or rest_bits.any() or f_in.read(1):
            raise Exception('encoded file invalid: unexpected trailing data')
        return crc

    def restore_tree(self, tree: bytes, pos: int, code: str) -> int:
        """Parse the node at `pos`, fill the table of codes and return the position after the node."""
        if pos >= len(tree):
            raise Exception('header is invalid')
        if tree[pos] == ord('0'):
            pos = self.restore_tree(tree, pos + 1, code + '0')
            return self.restore_tree(tree, pos, code + '1')
        elif tree[pos] == ord('1'):
            if pos + 1 >= len(tree):
                raise Exception('header is invalid')
            self.table_of_codes[code] = tree[pos + 1]
            return pos + 2
        else:
            raise Exception("Here must be a '0' or '1', not a letter")

    def read_header(self, file) -> tuple[bytes, int]:
        if file.read(len(MAGIC)) != MAGIC:
            raise Exception('not a Huffman compressed file')
        version = int.from_bytes(file.read(1), 'big')
        if version != FORMAT_VERSION:
            raise Exception(f'unsupported format version {version}')
        self.symbols_count = int.from_bytes(file.read(8), 'big')
        self.crc = int.from_bytes(file.read(4), 'big')
        tree_bytes = int.from_bytes(file.read(2), 'big')
        tree = file.read(tree_bytes)
        if len(tree) != tree_bytes:
            raise Exception('encoded file is truncated')
        return tree, len(MAGIC) + 1 + 8 + 4 + 2 + tree_bytes
