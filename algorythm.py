import node


class Algorythm:
    def __init__(self):
        self.nodes = []
        self.codes = {}
        self.freq = {}

    def compress_str(self, source, debug):
        self.define_freq(source)

        for k, v in self.freq.items():
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

        for k, v in self.freq.items():
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
        d = self.freq
        t = self.codes
        print('letter\tfrequency\tcode')
        for k, v in d.items():
            print(k + '\t' + str(v) + '\t' + t[k])

    def decode(encoded, table):
        decoded = ''
        while len(encoded) > 0:
            found = False
            for k, v in table.items():
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
        return ''.join(self.codes[ch] for ch in text)

    def create_table(self, node, code):
        if node.left is None and node.right is None:
            self.codes[node.letter] = ''.join(str(x) for x in code)
        else:
            self.create_table(node.left, code + '0')
            self.create_table(node.right, code + '1')

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
        d = self.freq
        for ch in list(s):
            d[ch] = 1 if ch not in d.keys() else d[ch] + 1
