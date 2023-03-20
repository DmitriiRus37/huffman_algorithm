class Node:
    def __init__(self, **kwargs):
        id = None
        if 'letter' in kwargs and 'freq' in kwargs:
            self.letter = kwargs['letter']
            self.freq = kwargs['freq']
            self.left = None
            self.right = None
        elif 'left' in kwargs and 'right' in kwargs:
            self.left = kwargs['left']
            self.right = kwargs['right']
            self.freq = self.left.freq + self.right.freq


def compress_str(source, debug):
    nodes = []
    freq_dict = {}
    define_freq(source, freq_dict)

    for k, v in freq_dict.items():
        nodes.append(Node(letter=k, freq=v))
    create_huffman_tree(nodes)
    table = {}
    create_table(table, nodes[0], '')
    if debug:
        debug_info(freq_dict, table)
    return encode(source, table)


def compress_file(source, dest):
    nodes = []
    text = ''
    freq_dict = {}
    with open(source, "r") as f:
        for line in f:
            text += line
            define_freq(line, freq_dict)

    for k, v in freq_dict.items():
        nodes.append(Node(letter=k, freq=v))
    create_huffman_tree(nodes)
    table = {}
    create_table(table, nodes[0], '')
    encoded_text = encode(text, table)
    with open(dest + 'encoded', "w") as f:
        f.write(encoded_text)
    # decoded_text = decode(encoded_text, table)
    # with open(dest + 'decoded', "w") as f:
    #     f.write(decoded_text)


def debug_info(d, t):
    print('letter\tfrequency\tcode')
    for k, v in d.items():
        print(k + '\t' + str(v) + '\t' +  t[k])


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


def encode(text, table):
    return ''.join(table[ch] for ch in text)


def create_table(table, node, code):
    if node.left is None and node.right is None:
        table[node.letter] = ''.join(str(x) for x in code)
    else:
        create_table(table, node.left, code + '0')
        create_table(table, node.right, code + '1')


def create_huffman_tree(nodes):
    if len(nodes) == 1:
        return nodes
    else:
        nodes.sort(key=lambda x: x.freq)
        parent = Node(left=nodes[0], right=nodes[1])
        nodes.append(parent)
        del nodes[0]
        del nodes[0]
        create_huffman_tree(nodes)


def define_freq(s: str, d: dict):
    for ch in list(s):
        d[ch] = 1 if ch not in d.keys() else d[ch] + 1

