from io import StringIO


def add_pad(string: str):
    padding = 8 - len(string) % 8
    if padding == 8:
        padding = 0
    return '{0:08b}'.format(padding) + string + '0' * padding


def create_huffman_tree(nodes):
    if len(nodes) == 1:
        return nodes
    else:
        nodes.sort(key=lambda x: x.freq)
        parent = Algorythm.Node(left=nodes[0], right=nodes[1])
        nodes.append(parent)
        del nodes[0]
        del nodes[0]
        create_huffman_tree(nodes)


class Algorythm:

    def __init__(self):
        self.table_of_codes = {}
        self.char_freq = {}

    class Node:
        def __init__(self, **kwargs):
            if 'letter' in kwargs and 'freq' in kwargs:
                self.letter = kwargs['letter']
                self.freq = kwargs['freq']
                self.left = None
                self.right = None
            elif 'left' in kwargs and 'right' in kwargs:
                self.left = kwargs['left']
                self.right = kwargs['right']
                self.freq = self.left.freq + self.right.freq

    def add_char_info(self, string):
        alphabet_length = len(self.table_of_codes.keys())

        # 4 bytes to store count of symbols in alphabet
        info = '{0:32b}'.format(alphabet_length).replace(' ', '0')

        # 4 bytes for every symbol
        # 4 bytes for every symbol code (there is '1' before every symbol code)
        # for exemaple: code is '0001'; it will be '10001'
        # (symbol_1, symbol_2, symbol_n) (code_1, code_2, code_n)
        symbols = ''
        symbol_codes = ''
        for k, v in self.table_of_codes.items():
            symbols += '{0:32b}'.format(ord(k)).replace(' ', '0')
            symbol_codes += ('1' + v).rjust(32, '0')
        return info + symbols + symbol_codes + string

    def encode(self, file):
        bits_io = StringIO()
        [bits_io.write(''.join(self.table_of_codes[ch] for ch in line)) for line in file]
        bits = add_pad(bits_io.getvalue())
        bits = self.add_char_info(bits)
        b_arr = bytearray()
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            int_val = int(byte, 2)
            b_arr.append(int_val)
        return b_arr

    def compress(self, source, dest):
        self.define_freq(source)
        nodes = [self.Node(letter=k, freq=v) for k, v in self.char_freq.items()]
        create_huffman_tree(nodes)
        self.create_table_of_codes(nodes[0], '')
        with open(source, "r") as f_in, open(dest, "wb") as f_out:
            byte_arr = self.encode(f_in)
            f_out.write(bytes(byte_arr))

    def define_freq(self, path: str):
        d = self.char_freq
        with open(path, "r") as f:
            for line in f:
                for ch in list(line):
                    d[ch] = d[ch] + 1 if ch in d.keys() else 1

    def get_table_info(self):
        print('letter\tfrequency\tcode')
        for k, v in self.char_freq.items():
            print(k + '\t' + str(v) + '\t' + self.table_of_codes[k])

    def create_table_of_codes(self, n, code):
        if n.left == n.right:
            self.table_of_codes[n.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table_of_codes(n.left, code + '0')
            self.create_table_of_codes(n.right, code + '1')
