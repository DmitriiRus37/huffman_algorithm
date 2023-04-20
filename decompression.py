import os
import time
from io import StringIO

from node import Node


class Decompression:
    def __init__(self):
        self.table_of_codes = {}
        self.bit_string = ''
        self.table_of_codes = {}
        self.nodes = []
        self.table_of_codes = {}

    class WrapValue:
        def __init__(self, val):
            self.val = val

    def decompress(self, source: str, dest: str):
        start_decompress_time = time.time()
        file_str = StringIO()
        with open(source, "rb") as f:
            header = self.read_header(f)
            header = self.WrapValue(header)
            root_node = Node(left=None, right=None)
            self.nodes.append(root_node)
            self.restore_tree(root_node, header, '')

            start_read_bytes_time = time.time()
            byte = f.read(1)
            while len(byte) > 0:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                file_str.write(bits)
                byte = f.read(1)
        self.bit_string = file_str.getvalue()
        print(f"--- {time.time() - start_read_bytes_time} seconds to read all bytes from file ---")
        self.remove_padding()
        self.decode(dest)
        print(f"--- {time.time() - start_decompress_time} seconds to decompress ---")
        input_size = os.path.getsize(source)
        output_size = os.path.getsize(dest)
        compress_percent = "{:.2f}".format(input_size / output_size * 100)
        print(f"--- Compression: {compress_percent} % ---")

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

    def read_header(self, file):
        header_bytes = int(process_4_bytes(file), 2)
        header_bytes = self.WrapValue(header_bytes)
        ba = read_bytes_to_bytearray(header_bytes.val, file)
        return ba.decode('utf8', errors='strict')

    def decode(self, dest: str):
        start_decode_time = time.time()
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
        print(f"--- {time.time() - start_decode_time} seconds to decode file and write it to dest ---")

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
