def add_pad(string: str):
    padding = 8 - len(string) % 8
    if padding == 8:
        padding = 0
    return '{0:08b}'.format(padding) + string + '0' * padding


class Algorythm:
    def __init__(self):
        self.nodes = []
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
        info = ''
        alphabet_length = len(self.table_of_codes.keys())

        # 4 bytes to store count of symbols in alphabet
        info += '{0:32b}'.format(alphabet_length).replace(' ', '0')

        # 4 bytes for every symbol
        # 4 bytes for every symbol code (there is '1' before every symbol code)
        # for exemaple: code is '0001'; it will be '10001'
        # (symbol_1, symbol_2, symbol_n) (code_1, code_2, code_n)
        symbols = ''
        symbol_codes = ''
        for k, v in self.table_of_codes.items():
            symbols += '{0:32b}'.format(ord(k)).replace(' ', '0')
            # code =
            symbol_codes += ('1' + v).rjust(32, '0')
        return info + symbols + symbol_codes + string

    def encode(self, text):
        bit_string = ''.join(self.table_of_codes[ch] for ch in text)
        bit_string = add_pad(bit_string)
        bit_string = self.add_char_info(bit_string)
        b_arr = bytearray()
        for i in range(0, len(bit_string), 8):
            byte = bit_string[i:i + 8]
            int_val = int(byte, 2)
            b_arr.append(int_val)
        return b_arr

    def compress(self, source, dest):
        text = ''
        with open(source, "r") as f_in, open(dest + '_encoded', "wb") as f_out:
            for line in f_in:
                text += line
                self.define_freq(line)

            for k, v in self.char_freq.items():
                self.nodes.append(self.Node(letter=k, freq=v))
            self.create_huffman_tree()
            self.create_table_of_codes(self.nodes[0], '')
            byte_arr = self.encode(text)
            f_out.write(bytes(byte_arr))

    def get_table_info(self):
        print('letter\tfrequency\tcode')
        for k, v in self.char_freq.items():
            print(k + '\t' + str(v) + '\t' + self.table_of_codes[k])

    def create_table_of_codes(self, n, code):
        if n.left is None and n.right is None:
            self.table_of_codes[n.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table_of_codes(n.left, code + '0')
            self.create_table_of_codes(n.right, code + '1')

    def create_huffman_tree(self):
        if len(self.nodes) == 1:
            return self.nodes
        else:
            self.nodes.sort(key=lambda x: x.freq)
            parent = self.Node(left=self.nodes[0], right=self.nodes[1])
            self.nodes.append(parent)
            del self.nodes[0]
            del self.nodes[0]
            self.create_huffman_tree()

    def define_freq(self, s: str):
        d = self.char_freq
        for ch in list(s):
            d[ch] = 1 if ch not in d.keys() else d[ch] + 1
