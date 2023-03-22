from io import StringIO
import time


class Algorythm:
    def __init__(self):
        self.table_of_codes = {}
        self.bit_string = ''

    def get_table_of_codes(self, f):
        bits = [bin(ord(f.read(1)))[2:].rjust(8, '0') for i in range(4)]
        bits = ''.join(bits)
        alphabet_count = int("".join(i for i in bits), 2)

        chars = []
        char_codes = []
        for i in range(alphabet_count):
            bits = process_4_bytes(f)
            char = int(bits, 2)
            chars.append(chr(char))

        for i in range(alphabet_count):
            bits = process_4_bytes(f)
            char_codes.append(bits[bits.index('1') + 1:])

        for i in range(alphabet_count):
            self.table_of_codes[char_codes[i]] = chars[i]

    def decompress(self, source: str, dest: str):
        start_decompress_time = time.time()
        file_str = StringIO()
        with open(source, "rb") as f:
            self.get_table_of_codes(f)
            byte = f.read(1)
            start_read_bytes_time = time.time()
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

    def decode(self, dest):
        start_decode_time = time.time()
        current_code = ''
        file_str = StringIO()
        for bit in self.bit_string:
            current_code += bit
            if current_code in self.table_of_codes:
                file_str.write(self.table_of_codes[current_code])
                current_code = ''
        with open(dest, "w") as f:
            f.write(file_str.getvalue())
        print(f"--- {time.time() - start_decode_time} seconds to decode file and write it to dest ---")

    def remove_padding(self):
        byte = self.bit_string[:8]
        padding_bits = int(byte, 2)
        length = len(self.bit_string) - padding_bits
        self.bit_string = self.bit_string[8:length]


def process_4_bytes(f):
    bits1 = [bin(ord(f.read(1)))[2:].rjust(8, '0') for _ in range(4)]
    return ''.join(bits1)
