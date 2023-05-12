import os
import shutil
from io import StringIO
from helpers import print_time_spent, update_pbar, WrapValue
from node import Node
from tqdm import tqdm
from bitarray import bitarray


def add_pad(rem: int) -> tuple[bitarray, bitarray]:
    padding = (8 - rem) % 8
    return bitarray('{0:08b}'.format(padding)), bitarray('0' * padding)


def split_write_and_rem(bit_arr: bitarray) -> tuple[bitarray, bitarray]:
    length = len(bit_arr) - len(bit_arr) % 8
    return bit_arr[:length], bit_arr[length:]


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
    def encode_and_write(self, source, dest) -> None:
        input_file_size = os.path.getsize(source) / 1024 / 1024
        print(f'Size of input file: {str(input_file_size)} Mb')
        with open(file=source, mode='r') as f_in, open(file=dest, mode='wb') as f_out:
            # if file is large then we must split it and work with each piece separately
            # for example 1 Mb
            max_partition_size = 1
            part_size = max_partition_size
            # partitions = math.ceil(input_file_size / max_partition_size)
            # part_size = input_file_size / partitions
            bit_arr_remainder = bitarray()
            pbar = tqdm(total=self.symbols_count, desc="Encoded symbols", unit='symbols', unit_scale=True)
            while True:
                end_of_file = WrapValue(False)
                bit_arr = bit_arr_remainder + self.encode_file(f_in, part_size, end_of_file, pbar)
                bit_arr_to_write, bit_arr_remainder = split_write_and_rem(bit_arr)
                rem = len(bit_arr_remainder)
                f_out.write(bytes(bit_arr_to_write))
                if end_of_file.val:
                    break
            padding_info, padding_symbols = add_pad(rem)
            f_out.write(bytes(bit_arr_remainder + bitarray(padding_symbols)))
        tmp_file_name = 'tmp'
        with open(file=dest, mode='rb') as f_in, open(file=tmp_file_name, mode='wb') as f_out:
            header = self.add_header_info()
            f_out.write(header)
            f_out.write(bytes(padding_info))
            block_size = 1024 * 1024  # 1 Мб
            while True:
                partition = f_in.read(block_size)
                if not partition:
                    break
                f_out.write(partition)
        shutil.move(tmp_file_name, dest)

    def encode_file(self, file, part_size, end_of_file: WrapValue, pbar: tqdm) -> bitarray:
        bit_arr = bitarray()
        num_bytes = 0
        for line in file:
            for ch in line:
                bit_arr += self.table_of_codes[ch]
            update_pbar(len(line), pbar)
            b = line.encode('utf-8')
            num_bytes += len(b)
            if num_bytes / 1024 / 1024 > part_size:
                return bit_arr
        pbar.close()
        end_of_file.val = True
        return bit_arr

    def validate_header(self, header: str) -> None:
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
        self.encode_and_write(source, dest)

    def codes_01_to_bits(self) -> None:
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


