import os
from io import StringIO
from helpers import print_time_spent, update_pbar
from node import Node
from tqdm import tqdm
from bitarray import bitarray


def add_pad(bit_ar: bitarray) -> bitarray:
    padding = (8 - len(bit_ar) % 8) % 8
    return bitarray('{0:08b}'.format(padding)) + bit_ar + bitarray('0' * padding)


class Compression:

    def __init__(self):
        self.symbols_count = 0
        self.table_of_codes = {}
        self.char_freq = {}
        self.nodes = []

    def create_huffman_tree(self) -> None:
        while len(self.nodes) != 1:
            self.nodes.sort(key=lambda x: x.freq)
            parent = Node(left=self.nodes[0], right=self.nodes[1])
            self.nodes.append(parent)
            del self.nodes[:2]

    def add_header_info(self) -> bytes:
        symbol_codes = StringIO()
        if self.nodes[0] is not None:
            self.build_header(self.nodes[0], symbol_codes)
        else:
            raise Exception('There are no nodes to build header!!!')
        head = symbol_codes.getvalue()
        self.validate_header(head)
        head_encoded = head.encode('utf8')
        # 4 bytes to store count of other header bytes (without self 4 bytes)
        tree_info = len(head_encoded)
        info_encoded = tree_info.to_bytes(4, 'big')
        return info_encoded + head_encoded

    def build_header(self, node: Node, current_header: StringIO) -> None:
        if node.left == node.right is None:
            current_header.write('1' + node.letter)
        else:
            current_header.write('0')
            self.build_header(node.left, current_header)
            self.build_header(node.right, current_header)

    @print_time_spent(message="to encode file")
    def encode_file(self, file) -> bytes:
        bits_io = bitarray()
        pbar = tqdm(total=self.symbols_count, desc="Encoded symbols", unit='symbols', unit_scale=True)
        for line in file:
            for ch in line:
                bits_io += self.table_of_codes[ch]
            update_pbar(len(line), pbar)
        pbar.close()
        bits_io = add_pad(bits_io)
        arr_header = bytes(self.add_header_info())
        byte_arr = bytes(bits_io)
        return arr_header + byte_arr

    def validate_header(self, header) -> None:
        unique_symbols = len(self.char_freq.keys())
        zeros_count = unique_symbols - 1
        ones_count = unique_symbols
        if self.char_freq.keys().__contains__('0'):
            zeros_count += 1
        if self.char_freq.keys().__contains__('1'):
            ones_count += 1
        if header.count('1') != ones_count or header.count('0') != zeros_count:
            raise Exception('header is invalid')

    @print_time_spent(message="to compress file")
    def compress(self, source: str, dest: str) -> None:
        self.define_freq(source)
        self.nodes = [Node(letter=k, freq=v) for k, v in self.char_freq.items()]
        self.create_huffman_tree()
        if len(self.char_freq.keys()) == 1:
            self.create_table_of_codes(self.nodes[0], '0')
        else:
            self.create_table_of_codes(self.nodes[0], '')
        self.codes_01_to_bits()
        self.validate_table_of_codes()
        with open(source, "r") as f_in, open(dest, "wb") as f_out:
            #TODO make partitions here: piece writes to memory, then writes to out file
            byte_arr = self.encode_file(f_in)
            f_out.write(bytes(byte_arr))

    def codes_01_to_bits(self):
        for k, v in self.table_of_codes.items():
            self.table_of_codes[k] = bitarray(v)

    def validate_table_of_codes(self) -> None:
        for key, value in self.table_of_codes.items():
            if value == bitarray():
                raise Exception('symbol \"' + key + '\" doesn\'t have a code')

    @print_time_spent(message="to define symbols frequency")
    def define_freq(self, path: str) -> None:
        with open(path, "r") as f:
            pbar = tqdm(total=float(os.path.getsize(path) / 1024 / 1024),
                        unit="Mb", unit_scale=True,
                        desc="Read to define frequency")
            for line in f:
                for ch in list(line):
                    self.char_freq.setdefault(ch, 0)
                    self.char_freq[ch] += 1
                update_pbar(len(line.encode('utf-8')) / 1024 / 1024, pbar)
            pbar.close()
        if len(self.char_freq) == 0:
            raise Exception("Source file is empty")
        print(f"--- {len(self.char_freq)} different symbols ---")
        self.symbols_count = sum(v for v in self.char_freq.values())

    def create_table_of_codes(self, n: Node, code: str) -> None:
        if n.left == n.right is None:
            self.table_of_codes[n.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table_of_codes(n.left, code + '0')
            self.create_table_of_codes(n.right, code + '1')
