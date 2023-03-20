import node


class Algorythm:
    def __init__(self):
        self.nodes = []
        self.table_of_codes = {}
        self.char_freq = {}

    def compress_str(self, source, debug):
        self.define_freq(source)

        for k, v in self.char_freq.items():
            self.nodes.append(node.Node(letter=k, freq=v))
        self.create_huffman_tree()
        self.create_table(self.nodes[0], '')
        if debug:
            self.debug_info()
        return self.encode(source)

    def compress_file(self, source, dest):
        text = ''
        with open(source, "r") as f:
            for line in f:
                text += line
                self.define_freq(line)

        for k, v in self.char_freq.items():
            self.nodes.append(node.Node(letter=k, freq=v))
        self.create_huffman_tree()
        table = {}
        self.create_table(table, self.nodes[0], '')
        encoded_text = self.encode(text)
        with open(dest + 'encoded', "w") as f:
            f.write(encoded_text)
        # decoded_text = decode(encoded_text, table)
        # with open(dest + 'decoded', "w") as f:
        #     f.write(decoded_text)

    def debug_info(self):
        d = self.char_freq
        t = self.table_of_codes
        print('letter\tfrequency\tcode')
        for k, v in d.items():
            print(k + '\t' + str(v) + '\t' + t[k])

    def decode(self, encoded):
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
        return ''.join(self.table_of_codes[ch] for ch in text)

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
            self.nodes.sort(key=lambda x: x.char_freq)
            parent = node.Node(left=self.nodes[0], right=self.nodes[1])
            self.nodes.append(parent)
            del self.nodes[0]
            del self.nodes[0]
            self.create_huffman_tree()

    def define_freq(self, s: str):
        d = self.char_freq
        for ch in list(s):
            d[ch] = 1 if ch not in d.keys() else d[ch] + 1
