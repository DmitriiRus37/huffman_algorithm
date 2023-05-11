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

    @print_time_spent(message="to read all bytes from file")
    def read_from_file(self, file_name: str) -> tuple[bitarray, int]:
        with open(file_name, "rb") as f:
            header, header_bytes = self.read_header(f)
            header = WrapValue(header)
            root_node = Node(left=None, right=None)
            self.nodes.append(root_node)
            if len(header.val) == 2:
                self.restore_tree(root_node, header, '0')
            else:
                self.restore_tree(root_node, header, '')
            bit_array = bitarray()
            bit_array.fromfile(f)
            return bit_array, header_bytes

    @print_time_spent(message="to decompress")
    def decompress(self, source: str, dest: str) -> None:
        bit_arr, header_bytes = self.read_from_file(source)
        pbar = tqdm(total=float(os.path.getsize(source) / 1024 / 1024),
                    unit="Mb", unit_scale=True,
                    desc="Decoded")
        update_pbar(header_bytes / 1024 / 1024, pbar)
        self.bit_string = bit_arr.to01()
        self.remove_padding()
        self.decode(pbar, dest)

    def set_letter_to_a_node(self, node: Node, letter: str, code: str) -> None:
        node.letter = letter
        self.table_of_codes[code] = letter

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

    @staticmethod
    def read_header(file) -> tuple[str, int]:
        header_bytes = int(read_4_bytes_to_bits(file), 2)
        header_bytes = WrapValue(header_bytes)
        ba = read_bytes_to_bytearray(header_bytes.val, file)
        return ba.decode('utf8', errors='strict'), header_bytes.val + 4

    @print_time_spent(message="to decode file and write it to dest")
    def decode(self, pbar, dest: str) -> None:
        current_code = ''
        file_str = StringIO()
        bits_count = 0
        for bit in self.bit_string:
            current_code += bit
            bits_count += 1
            if bits_count == 8:
                update_pbar(1 / 1024 / 1024, pbar)
                bits_count = 0
            if current_code in self.table_of_codes:
                symbol = self.table_of_codes[current_code]
                file_str.write(symbol)
                current_code = ''
        update_pbar(bits_count / 8 / 1024 / 1024, pbar)
        pbar.close()
        with open(dest, "w") as f:
            f.write(file_str.getvalue())

    def remove_padding(self) -> None:
        byte = self.bit_string[:8]
        padding_bits = int(byte, 2)
        length = len(self.bit_string) - padding_bits
        self.bit_string = self.bit_string[8:length]


def read_byte_to_val(f) -> str:
    return bin(ord(f.read(1)))[2:]


def read_byte_to_char(f) -> str:
    b = f.read(1)
    char = str(b, encoding='utf-8')
    return char


def read_4_bytes_to_bits(f) -> str:
    bits = [read_byte_to_val(f).rjust(8, '0') for _ in range(4)]
    return ''.join(bits)


def read_bytes_to_bytearray(count: int, f) -> bytearray:
    return bytearray(f.read(count))
