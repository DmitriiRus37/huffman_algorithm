import heapq
import os
import zlib
from collections import Counter
from io import BytesIO
from helpers import print_time_spent, update_pbar
from node import Node
from tqdm import tqdm
from bitarray import bitarray

# File format (all integers big-endian):
#   4 bytes  MAGIC
#   1 byte   FORMAT_VERSION
#   8 bytes  size of the original file in bytes
#   4 bytes  CRC32 of the original file
#   2 bytes  length of the serialized tree
#   N bytes  pre-order tree: b'0' - internal node, b'1' + raw byte - leaf
#   rest     encoded data, the last byte is padded with zero bits
MAGIC = b'HUFF'
FORMAT_VERSION = 1
PARTITION_SIZE = 1024 * 64  # 64 Kbyte


def split_write_and_rem(bit_arr: bitarray) -> tuple[bitarray, bitarray]:
    length = len(bit_arr) - len(bit_arr) % 8
    return bit_arr[:length], bit_arr[length:]


class Compression:

    def __init__(self):
        self.symbols_count = 0
        self.crc = 0
        self.table_of_codes = {}
        self.char_freq = {}
        self.nodes = []

    def create_huffman_tree(self) -> None:
        # the counter breaks ties between equal frequencies, so Nodes are never compared
        heap = [(node.freq, i, node) for i, node in enumerate(self.nodes)]
        heapq.heapify(heap)
        counter = len(heap)
        while len(heap) > 1:
            _, _, left = heapq.heappop(heap)
            _, _, right = heapq.heappop(heap)
            parent = Node(left=left, right=right)
            heapq.heappush(heap, (parent.freq, counter, parent))
            counter += 1
        self.nodes = [heap[0][2]] if heap else []

    def add_header_info(self) -> bytes:
        symbol_codes = BytesIO()
        if self.nodes:
            self.build_header(self.nodes[0], symbol_codes)
        tree = symbol_codes.getvalue()
        self.validate_header(tree)
        return (MAGIC
                + FORMAT_VERSION.to_bytes(1, 'big')
                + self.symbols_count.to_bytes(8, 'big')
                + self.crc.to_bytes(4, 'big')
                + len(tree).to_bytes(2, 'big')
                + tree)

    def build_header(self, node: Node, current_header: BytesIO) -> None:
        if node.left == node.right is None:
            current_header.write(b'1' + bytes([node.letter]))
        else:
            current_header.write(b'0')
            self.build_header(node.left, current_header)
            self.build_header(node.right, current_header)

    @print_time_spent(message="to encode file")
    def encode_and_write(self, source, dest) -> None:
        input_file_size = os.path.getsize(source) / 1024 / 1024
        print(f'Size of input file: {str(input_file_size)} Mb')
        with open(file=source, mode='rb') as f_in, open(file=dest, mode='wb') as f_out:
            f_out.write(self.add_header_info())
            bit_arr_remainder = bitarray()
            pbar = tqdm(total=self.symbols_count, desc="Encoded symbols", unit='symbols', unit_scale=True)
            while True:
                chunk = f_in.read(PARTITION_SIZE)
                if not chunk:
                    break
                bit_arr = bit_arr_remainder
                bit_arr.encode(self.table_of_codes, chunk)
                update_pbar(len(chunk), pbar)
                bit_arr_to_write, bit_arr_remainder = split_write_and_rem(bit_arr)
                f_out.write(bytes(bit_arr_to_write))
            pbar.close()
            # bytes() pads the last incomplete byte with zero bits
            f_out.write(bytes(bit_arr_remainder))

    def validate_header(self, header: bytes) -> None:
        # every leaf takes 2 bytes, every internal node (leaves - 1 of them) takes 1 byte
        unique_symbols = len(self.char_freq)
        expected_len = 3 * unique_symbols - 1 if unique_symbols else 0
        if len(header) != expected_len:
            raise Exception('header is invalid')

    @print_time_spent(message="to compress file")
    def compress(self, source: str, dest: str) -> None:
        self.define_freq(source)
        self.nodes = [Node(letter=k, freq=v) for k, v in self.char_freq.items()]
        self.create_huffman_tree()
        if len(self.char_freq) == 1:
            self.create_table_of_codes(self.nodes[0], '0')
        elif self.char_freq:
            self.create_table_of_codes(self.nodes[0], '')
        self.codes_01_to_bits()
        self.validate_table_of_codes()
        self.encode_and_write(source, dest)

    def codes_01_to_bits(self) -> None:
        for k, v in self.table_of_codes.items():
            self.table_of_codes[k] = bitarray(v)

    def validate_table_of_codes(self) -> None:
        for key, value in self.table_of_codes.items():
            if value == bitarray():
                raise Exception(f'symbol {key} doesn\'t have a code')

    @print_time_spent(message="to define symbols frequency")
    def define_freq(self, path: str) -> None:
        chunk_size = 1024 * 1024  # 1 Mb
        counter = Counter()
        crc = 0
        with open(path, "rb") as f:
            pbar = tqdm(total=float(os.path.getsize(path) / 1024 / 1024),
                        unit="Mb", unit_scale=True,
                        desc="Read to define frequency")
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                counter.update(chunk)
                crc = zlib.crc32(chunk, crc)
                update_pbar(len(chunk) / 1024 / 1024, pbar)
            pbar.close()
        self.char_freq = dict(counter)
        self.crc = crc
        print(f"--- {len(self.char_freq)} different symbols ---")
        self.symbols_count = sum(self.char_freq.values())

    def create_table_of_codes(self, n: Node, code: str) -> None:
        if n.left == n.right is None:
            self.table_of_codes[n.letter] = code
        else:
            self.create_table_of_codes(n.left, code + '0')
            self.create_table_of_codes(n.right, code + '1')
