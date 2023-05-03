from io import StringIO

from bitarray import bitarray

from helpers import print_time_spent, WrapValue
from node import Node


class Decompression:
    def __init__(self):
        self.table_of_codes = {}
        self.bit_string = ''
        self.table_of_codes = {}
        self.nodes = []
        self.table_of_codes = {}

    @print_time_spent(message="to read all bytes from file")
    def read_from_file(self, file_name: str) -> bitarray:
        with open(file_name, "rb") as f:
            header = self.read_header(f)
            header = WrapValue(header)
            root_node = Node(left=None, right=None)
            self.nodes.append(root_node)
            if len(header.val) == 2:
                self.restore_tree(root_node, header, '0')
            else:
                self.restore_tree(root_node, header, '')
            bit_array = bitarray()
            bit_array.fromfile(f)
            return bit_array

    @print_time_spent(message="to decompress")
    def decompress(self, source: str, dest: str):
        self.bit_string = self.read_from_file(source).to01()
        self.remove_padding()
        self.decode(dest)

    def set_letter_to_a_node(self, node: Node, letter: str, code: str):
        node.letter = letter
        self.table_of_codes[code] = letter

    def restore_tree(self, node: Node, symbol_str: WrapValue, code: str):
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
    def read_header(file):
        header_bytes = int(process_4_bytes(file), 2)
        header_bytes = WrapValue(header_bytes)
        ba = read_bytes_to_bytearray(header_bytes.val, file)
        return ba.decode('utf8', errors='strict')

    @print_time_spent(message="to decode file and write it to dest")
    def decode(self, dest: str):
        current_code = ''
        file_str = StringIO()
        for bit in self.bit_string:
            current_code += bit
            if current_code in self.table_of_codes:
                symbol = self.table_of_codes[current_code]
                file_str.write(symbol)
                current_code = ''
        with open(dest, "w") as f:
            f.write(file_str.getvalue())

    def remove_padding(self):
        byte = self.bit_string[:8]
        padding_bits = int(byte, 2)
        length = len(self.bit_string) - padding_bits
        self.bit_string = self.bit_string[8:length]


def read_byte_to_val(f):
    return bin(ord(f.read(1)))[2:]


def read_byte_to_char(f):
    b = f.read(1)
    char = str(b, encoding='utf-8')
    return char


def process_4_bytes(f):
    bits1 = [read_byte_to_val(f).rjust(8, '0') for _ in range(4)]
    return ''.join(bits1)


def read_bytes_to_bytearray(count: int, f):
    return bytearray(f.read(count))
