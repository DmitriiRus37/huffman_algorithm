import os
from io import StringIO
import time


def add_pad(string: str):
    padding = 8 - len(string) % 8
    if padding == 8:
        padding = 0
    return '{0:08b}'.format(padding) + string + '0' * padding


class Compression:

    def __init__(self):
        self.table_of_codes = {}
        self.char_freq = {}
        self.nodes = []


    def create_huffman_tree(self):
        if len(self.nodes) == 1:
            return
        else:
            self.nodes.sort(key=lambda x: x.freq)
            parent = Compression.Node(left=self.nodes[0], right=self.nodes[1])
            self.nodes.append(parent)
            del self.nodes[0]
            del self.nodes[0]
            self.create_huffman_tree()

    def add_header_info(self):
        symbol_codes = StringIO()
        if self.nodes[0] is not None:
            self.build_header(self.nodes[0], symbol_codes)
        else:
            raise Exception('There are no nodes to build header!!!')
        head = symbol_codes.getvalue()
        head_encoded = head.encode('utf8')
        # 4 bytes to store count of other header bytes (without self 4 bytes)
        tree_info = len(head_encoded)
        info_encoded = tree_info.to_bytes(4, 'big')
        return info_encoded + head_encoded

    def build_header(self, node: Node, current_header: StringIO):
        if node.left is None and node.right is None:
            current_header.write('1' + node.letter)
        else:
            current_header.write('0')
            self.build_header(node.left, current_header)
            self.build_header(node.right, current_header)

    def check_right_node(self, node, current_header):
        if node.letter is None:
            self.build_header(node, current_header)
        else:
            current_header.write('1' + node.letter)

    def encode(self, file):
        start_encode_time = time.time()
        bits_io = StringIO()
        [bits_io.write(''.join(self.table_of_codes[ch] for ch in line)) for line in file]
        bits = add_pad(bits_io.getvalue())
        arr_header = bytearray(self.add_header_info())
        b_arr = bytearray((int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8))
        print(f"--- {time.time() - start_encode_time} seconds to encode file ---")
        return arr_header + b_arr

    def compress(self, source, dest):
        start_compress_time = time.time()
        self.define_freq(source)
        self.nodes = [self.Node(letter=k, freq=v) for k, v in self.char_freq.items()]
        self.create_huffman_tree()
        self.create_table_of_codes(self.nodes[0], '')
        with open(source, "r") as f_in, open(dest, "wb") as f_out:
            byte_arr = self.encode(f_in)
            f_out.write(bytes(byte_arr))
        print(f"--- {time.time() - start_compress_time} seconds to compress file ---")
        input_size = os.path.getsize(source)
        output_size = os.path.getsize(dest)
        compress_percent = "{:.2f}".format(output_size / input_size * 100)
        print(f"--- Compression: {compress_percent} % ---")

    def define_freq(self, path: str):
        start_define_freq_time = time.time()
        d = self.char_freq
        with open(path, "r") as f:
            for line in f:
                for ch in list(line):
                    d[ch] = d[ch] + 1 if ch in d.keys() else 1
        print(f"--- {len(self.char_freq)} different symbols ---")
        print(f"--- {time.time() - start_define_freq_time} seconds to define symbols frequency ---")

    def create_table_of_codes(self, n, code):
        if n.left == n.right:
            self.table_of_codes[n.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table_of_codes(n.left, code + '0')
            self.create_table_of_codes(n.right, code + '1')
