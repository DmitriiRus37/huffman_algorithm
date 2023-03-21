import node


def pad_bit_string(string: str):
    padding = 8 - len(string) % 8
    padding_byte = '{0:08b}'.format(padding)
    return padding_byte + string + '0' * padding


class Algorythm:
    def __init__(self):
        self.nodes = []
        self.table_of_codes = {}
        self.char_freq = {}

    def compress(self, source, dest):
        text = ''
        with open(source, "r") as f:
            for line in f:
                text += line
                self.define_freq(line)

        for k, v in self.char_freq.items():
            self.nodes.append(node.Node(letter=k, freq=v))
        self.create_huffman_tree()
        self.create_table(self.nodes[0], '')
        byte_arr = self.encode(text)
        with open(dest + '_encoded', "wb") as f:
            f.write(bytes(byte_arr))
        self.write_table_info(dest)

    def get_table_info(self):
        print('letter\tfrequency\tcode')
        for k, v in self.char_freq.items():
            print(k + '\t' + str(v) + '\t' + self.table_of_codes[k])

    def write_table_info(self, dest):
        with open(dest + '_table', "w") as f:
            f.write('letter\tfrequency\tcode\n')
            for k, v in self.char_freq.items():
                if k == '\n':
                    f.write('bl' + '\t' + str(v) + '\t' + self.table_of_codes[k] + '\n')
                elif k == ' ':
                    f.write('sp' + '\t' + str(v) + '\t' + self.table_of_codes[k] + '\n')
                else:
                    f.write(k + '\t' + str(v) + '\t' + self.table_of_codes[k] + '\n')

    def decode(self):
        decoded = ''
        while len(encoded) > 0:
            found = False
            for k, v in self.table_of_codes.items():
                code_len = len(v)
                if encoded[:code_len] == v:
                    decoded += k
                    found = True
                    encoded = encoded[code_len:]
                    break
            if not found:
                raise Exception('code not found')
        return decoded

    def encode(self, text):
        bit_string = ''.join(self.table_of_codes[ch] for ch in text)
        bit_string = pad_bit_string(bit_string)
        b_arr = bytearray()
        for i in range(0, len(bit_string), 8):
            byte = bit_string[i:i + 8]
            int_val = int(byte, 2)
            b_arr.append(int_val)
        return b_arr

    def create_table(self, n, code):
        if n.left is None and n.right is None:
            self.table_of_codes[n.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table(n.left, code + '0')
            self.create_table(n.right, code + '1')

    def create_huffman_tree(self):
        if len(self.nodes) == 1:
            return self.nodes
        else:
            self.nodes.sort(key=lambda x: x.freq)
            parent = node.Node(left=self.nodes[0], right=self.nodes[1])
            self.nodes.append(parent)
            del self.nodes[0]
            del self.nodes[0]
            self.create_huffman_tree()

    def define_freq(self, s: str):
        d = self.char_freq
        for ch in list(s):
            d[ch] = 1 if ch not in d.keys() else d[ch] + 1
