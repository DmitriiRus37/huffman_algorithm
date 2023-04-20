import filecmp
import os
import unittest
from unittest.mock import patch

import main


class TestApp(unittest.TestCase):

    def test_1(self):
        original_file_name = 'test_files/test1.txt'

        compressed_file_name = 'tmp_files/test1_zip'
        compress_args = [
            "",
            original_file_name,
            compressed_file_name
        ]
        with unittest.mock.patch('sys.argv', compress_args):
            main.main()

        decompressed_file_name = 'tmp_files/test1_res.txt'
        decompress_args = [
            "",
            "decode",
            compressed_file_name,
            decompressed_file_name
        ]
        with unittest.mock.patch('sys.argv', decompress_args):
            main.main()
        assert filecmp.cmp(original_file_name, decompressed_file_name)
        os.remove(compressed_file_name)
        os.remove(decompressed_file_name)

    def test_2(self):
        original_file_name = 'test_files/test2.xml'

        compressed_file_name = 'tmp_files/test2_zip'
        compress_args = [
            "",
            original_file_name,
            compressed_file_name
        ]
        with unittest.mock.patch('sys.argv', compress_args):
            main.main()

        decompressed_file_name = 'tmp_files/test2_res.xml'
        decompress_args = [
            "",
            "decode",
            compressed_file_name,
            decompressed_file_name
        ]
        with unittest.mock.patch('sys.argv', decompress_args):
            main.main()
        assert filecmp.cmp(original_file_name, decompressed_file_name)
        os.remove(compressed_file_name)
        os.remove(decompressed_file_name)

    def test_3(self):
        original_file_name = 'test_files/test3.txt'

        compressed_file_name = 'tmp_files/test3_zip'
        compress_args = [
            "",
            original_file_name,
            compressed_file_name
        ]
        with unittest.mock.patch('sys.argv', compress_args):
            main.main()

        decompressed_file_name = 'tmp_files/test3_res.txt'
        decompress_args = [
            "",
            "decode",
            compressed_file_name,
            decompressed_file_name
        ]
        with unittest.mock.patch('sys.argv', decompress_args):
            main.main()
        assert filecmp.cmp(original_file_name, decompressed_file_name)
        os.remove(compressed_file_name)
        os.remove(decompressed_file_name)
