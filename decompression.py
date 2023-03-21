class Algorythm:
    def __init__(self):
        self.table_of_codes = {}

    def get_table_of_codes(self, f):
        byte_tuple = (ord(f.read(1)), ord(f.read(1)), ord(f.read(1)), ord(f.read(1)))
        bits = ''
        for i in range(len(byte_tuple)):
            bits += bin(byte_tuple[i])[2:].rjust(8, '0')

        alphabet_count = 0
        for bit in bits:
            alphabet_count = (alphabet_count << 1) | int(bit)

        chars = []
        char_codes = []
        for i in range(alphabet_count):
            char_tuple = (ord(f.read(1)), ord(f.read(1)), ord(f.read(1)), ord(f.read(1)))
            bits = ''
            for i in range(len(char_tuple)):
                bits += bin(char_tuple[i])[2:].rjust(8, '0')
            char = 0
            for bit in bits:
                char = (char << 1) | int(bit)
            chars.append(chr(char))
        for i in range(alphabet_count):
            code_tuple = (ord(f.read(1)), ord(f.read(1)), ord(f.read(1)), ord(f.read(1)))
            bits = ''
            for i in range(len(code_tuple)):
                bits += bin(code_tuple[i])[2:].rjust(8, '0')
            char_codes.append(bits[bits.index('1') + 1:])
        for i in range(alphabet_count):
            self.table_of_codes[chars[i]] = char_codes[i]
        self.table_of_codes = {v: k for k, v in self.table_of_codes.items()}

    def decompress(self, source: str, dest: str):
        with open(source, "rb") as f:
            self.get_table_of_codes(f)
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
        current_code = ''
        for bit in bit_string:
            current_code += bit
            if current_code in self.table_of_codes:
                decoded_text += self.table_of_codes[current_code]
                current_code = ''
        with open(dest, "w") as f:
            f.write(decoded_text)


def remove_padding(bit_string):
    byte = bit_string[:8]
    padding_bits = int(byte, 2)
    length = len(bit_string) - padding_bits
    return bit_string[8:length]
