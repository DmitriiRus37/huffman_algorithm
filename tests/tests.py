import filecmp
import os
from unittest import TestCase
from unittest.mock import patch

from src import main


def get_args(original_file_name, compressed_file_name):
    return [
        "",
        original_file_name,
        compressed_file_name
    ]


def common(original_file_name, compressed_file_name, decompressed_file_name):
    compress_args = get_args(original_file_name, compressed_file_name)
    with patch('sys.argv', compress_args):
        main.main()

    decompress_args = [
        "",
        "decode",
        compressed_file_name,
        decompressed_file_name
    ]
    with patch('sys.argv', decompress_args):
        main.main()
    assert filecmp.cmp(original_file_name, decompressed_file_name, shallow=False), \
        f'{decompressed_file_name} differs from {original_file_name}'


def common_bytes(test_name, data: bytes):
    original_file_name = f'tmp_files/{test_name}_src'
    compressed_file_name = f'tmp_files/{test_name}_zip'
    decompressed_file_name = f'tmp_files/{test_name}_res'
    with open(original_file_name, 'wb') as f:
        f.write(data)
    try:
        common(original_file_name, compressed_file_name, decompressed_file_name)
    finally:
        for f in (original_file_name, compressed_file_name, decompressed_file_name):
            if os.path.isfile(f):
                os.remove(f)


class TestApp(TestCase):
    # Ran 6 tests in 133.561s

    def tearDown(self):
        for f in self.files_to_remove:
            if os.path.isfile(f):
                os.remove(f)

    def test_1(self):
        original_file_name = 'test_files/test1.txt'
        compressed_file_name = 'tmp_files/test1_zip'
        decompressed_file_name = 'tmp_files/test1_res.txt'
        self.files_to_remove = [compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_2(self):
        original_file_name = 'test_files/test2.xml'
        compressed_file_name = 'tmp_files/test2_zip'
        decompressed_file_name = 'tmp_files/test2_res.xml'
        self.files_to_remove = [compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_3(self):
        original_file_name = 'test_files/test3.txt'
        compressed_file_name = 'tmp_files/test3_zip'
        decompressed_file_name = 'tmp_files/test3_res.txt'
        self.files_to_remove = [compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_4(self):
        original_file_name = 'test_files/test4.txt'
        compressed_file_name = 'tmp_files/test4_zip'
        decompressed_file_name = 'tmp_files/test4_res.txt'
        self.files_to_remove = [compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_5(self):
        extended_file_name = 'test_files/test2.xml'
        original_file_name = 'test_files/test5.xml'
        if os.path.exists(original_file_name):
            os.remove(original_file_name)
        with open(extended_file_name, "r") as file1, open(original_file_name, "a") as file2:
            data = file1.read()
            [file2.write(data) for _ in range(5)]
        compressed_file_name = 'tmp_files/test5_zip'
        decompressed_file_name = 'tmp_files/test5_res.xml'
        self.files_to_remove = [original_file_name, compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_6(self):
        original_file_name = 'test_files/test6.txt'
        compressed_file_name = 'tmp_files/test6_zip'
        decompressed_file_name = 'tmp_files/test6_res.txt'
        self.files_to_remove = [compressed_file_name, decompressed_file_name]
        common(original_file_name, compressed_file_name, decompressed_file_name)

    def test_empty_file(self):
        self.files_to_remove = []
        common_bytes('empty', b'')

    def test_crlf_line_endings(self):
        self.files_to_remove = []
        common_bytes('crlf', b'first line\r\nsecond line\r\n\r\nlast\r')

    def test_binary_non_utf8(self):
        self.files_to_remove = []
        common_bytes('binary', b'caf\xc3\xa9 \xff\xfe\x00\x01 binary \x80\x81' * 100)
