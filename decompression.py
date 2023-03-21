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

    def decode(self, source: str, dest: str):
        decoded = ''

        with open(source, "r") as f:
            encoded_text = f.read()
            decoded_text = ''
            while len(encoded_text) > 0:
                found = False
                for k, v in self.table_of_codes.items():
                    if encoded_text.find(v) == 0:
                        decoded_text += k
                        encoded_text = encoded_text[len(v):]
                        found = True
                        break
                if not found:
                    raise Exception('code not found')
        with open(dest, 'w') as f:
            f.write(decoded_text)
