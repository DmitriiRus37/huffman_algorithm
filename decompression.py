import node


class Algorythm:
    def __init__(self):
        self.table_of_codes = {}

    def get_table_of_codes(self, source: str):
        with open(source.replace('encoded', '') + 'table', "r") as f:
            i = -1
            for line in f:
                i += 1
                if i == 0:
                    continue
                array = line.split('\t')
                if array[0] == 'bl':
                    self.table_of_codes['\n'] = array[2][:-1]
                elif array[0] == 'sp':
                    self.table_of_codes[' '] = array[2][:-1]
                else:
                    self.table_of_codes[array[0]] = array[2][:-1]
        self.table_of_codes = {v: k for k, v in self.table_of_codes.items()}

    def decompress(self, source: str, dest: str):
        decoded = ''

        with open(source, "rb") as f:
            bit_string = ''
            byte = f.read(1)
            while len(byte) > 0:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = f.read(1)

        bit_string = remove_padding(bit_string)
        self.decode(bit_string, dest)

    def decode(self, bit_string, dest):
        decoded_text = ''
        code = ''
        for bit in bit_string:
            code += bit
            if code in self.table_of_codes:
                decoded_text += self.table_of_codes[code]
                code = ''
        with open(dest, "w") as f:
            f.write(decoded_text)


def remove_padding(bit_string):
    byte = bit_string[:8]
    padding_bits = int(byte, 2)
    bit_string = bit_string[8:]

    length = len(bit_string) - padding_bits

    return bit_string[:length]
