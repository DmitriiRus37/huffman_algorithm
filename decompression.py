import os
from io import StringIO
from bitarray import bitarray
from helpers import print_time_spent, WrapValue, update_pbar
from node import Node
from tqdm import tqdm


class Decompression:
    def __init__(self):
        self.table_of_codes = {}
        self.bit_string = ''
        self.table_of_codes = {}
        self.nodes = []
        self.table_of_codes = {}
        self.block = bitarray()
        self.padding_bits = 0
        self.rest_bits = bitarray()
        self.rest_code = ''

    @print_time_spent(message="to read all bytes from file")
    def read_from_file(self, f) -> int:
        header, header_bytes = self.read_header(f)
        header = WrapValue(header)
        root_node = Node(left=None, right=None)
        self.nodes.append(root_node)
        if len(header.val) == 2:
            self.restore_tree(root_node, header, '0')
        else:
            self.restore_tree(root_node, header, '')
        return header_bytes

    @print_time_spent(message="to decompress")
    def decompress(self, source: str, dest: str) -> None:
        with open(source, "rb") as f:
            partition_size = 1024 * 64
            header_bytes = self.read_from_file(f)
            pbar = tqdm(total=float(os.path.getsize(source) / 1024 / 1024),
                        unit="Mb", unit_scale=True,
                        desc="Decoded")
            update_pbar(header_bytes / 1024 / 1024, pbar)

            self.padding_bits = int.from_bytes(f.read(1), 'big')
            self.block.frombytes(f.read(partition_size))
            if self.block == bitarray():
                raise Exception('Encrypted file contains only header')
            while True:
                next_block = bitarray()
                next_block.frombytes(f.read(partition_size))
                if next_block == bitarray():
                    self.decode_last_block(dest)
                    update_pbar(self.block.nbytes / 1024 / 1024, pbar)
                    break
                self.decode_block(dest)
                update_pbar(self.block.nbytes / 1024 / 1024, pbar)
                self.block = next_block
            pbar.close()

    def restore_tree(self, node: Node, symbol_str: WrapValue, code: str) -> None:
        if symbol_str.val == '':
            return
        symbol = symbol_str.val[0]
        symbol_str.val = symbol_str.val[1:]
        if symbol == '0':
            left_node = Node(left=None, right=None)
            node.left = left_node
            self.restore_tree(left_node, symbol_str, code + '0')
            right_node = Node(left=None, right=None)
            node.right = right_node
            self.restore_tree(right_node, symbol_str, code + '1')
        elif symbol == '1':
            symbol = symbol_str.val[0]
            symbol_str.val = symbol_str.val[1:]
            self.set_letter_to_a_node(node, symbol, code)
        else:
            raise Exception("Here must be a '0' or '1', not a letter")

    def set_letter_to_a_node(self, node: Node, letter: str, code: str) -> None:
        node.letter = letter
        self.table_of_codes[code] = letter

    @staticmethod
    def read_header(file) -> tuple[str, int]:
        header_bytes = read_4_bytes_to_int(file)
        ba = read_to_bytes(header_bytes, file)
        return ba.decode('utf8', errors='strict'), header_bytes + 4

    def decode_block(self, dest: str) -> None:
        block_size_bits = len(self.block)
        file_str = StringIO()
        self.get_symbols(self.rest_bits + self.block[:block_size_bits-7], file_str)
        self.rest_bits = self.block[block_size_bits-7:]
        with open(dest, "a") as f:
            f.write(file_str.getvalue())

    def decode_last_block(self, dest: str) -> None:
        block_size_bits = len(self.block)
        file_str = StringIO()
        self.get_symbols(self.rest_bits + self.block[:block_size_bits - self.padding_bits], file_str)
        if self.rest_code != '':
            raise Exception('encoded file invalid!!!')
        with open(dest, "a") as f:
            f.write(file_str.getvalue())

    def get_symbols(self, bitar, file_str):
        for bit in bitar:
            self.rest_code += '0' if bit == 0 else '1'
            if self.rest_code in self.table_of_codes:
                symbol = self.table_of_codes[self.rest_code]
                file_str.write(symbol)
                self.rest_code = ''


def read_4_bytes_to_int(f) -> int:
    return int.from_bytes(f.read(4), 'big')


def read_to_bytes(count: int, f) -> bytes:
    return bytes(f.read(count))
