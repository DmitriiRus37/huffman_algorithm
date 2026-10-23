import zlib
from pathlib import Path

import pytest
from bitarray import bitarray

from huffman import Compression, Decompression, HuffmanError, HuffmanFormatError, get_compression_info
from huffman.compression import FORMAT_VERSION, MAGIC, split_write_and_rem
from huffman.node import Node


def archive(tree: bytes, data: bytes = b'', count: int = 0, crc: int = 0, version: int = FORMAT_VERSION) -> bytes:
    return (MAGIC + version.to_bytes(1, 'big') + count.to_bytes(8, 'big') + crc.to_bytes(4, 'big')
            + len(tree).to_bytes(2, 'big') + tree + data)


def decompress_bytes(tmp_path: Path, payload: bytes) -> bytes:
    src = tmp_path / 'in.huff'
    src.write_bytes(payload)
    Decompression(verbose=False).decompress(str(src), str(tmp_path / 'out'))
    return (tmp_path / 'out').read_bytes()


def test_header_layout_and_codes(tmp_path):
    src = tmp_path / 'src'
    src.write_bytes(b'aaab')
    c = Compression(verbose=False)
    c.compress(str(src), str(tmp_path / 'out'))
    assert c.char_freq == {ord('a'): 3, ord('b'): 1}
    assert c.symbols_count == 4
    assert c.crc == zlib.crc32(b'aaab')
    assert sorted(len(v) for v in c.table_of_codes.values()) == [1, 1]
    data = (tmp_path / 'out').read_bytes()
    assert data[:4] == MAGIC and data[4] == FORMAT_VERSION
    assert int.from_bytes(data[5:13], 'big') == 4
    assert int.from_bytes(data[17:19], 'big') == 5  # '0' + two 2-byte leaves
    assert len(data) == 19 + 5 + 1


def test_hand_built_archive_decodes(tmp_path):
    # tree: internal('0'), leaf 'x' (code 0), leaf 'y' (code 1); data bits 0110 -> "xyyx"
    tree = b'0' + b'1x' + b'1y'
    bits = bitarray('0110')
    payload = archive(tree, bytes(bits), count=4, crc=zlib.crc32(b'xyyx'))
    assert decompress_bytes(tmp_path, payload) == b'xyyx'


@pytest.mark.parametrize('payload,match', [
    (archive(b'', version=9), 'unsupported format version 9'),
    (archive(b'0' + b'1x' + b'1y')[:-2], 'truncated'),
    (archive(b'0' + b'1x'), 'header is invalid'),
    (archive(b'0' + b'1x' + b'1'), 'header is invalid'),
    (archive(b'0' + b'1x' + b'2y'), "expected a '0' or '1'"),
    (archive(b'1x' + b'1y'), 'header is invalid'),
    (archive(b'', count=3), 'data for an empty source'),
    (archive(b'', b'\x00'), 'data for an empty source'),
    (archive(b'0' + b'1x' + b'1y', b'', count=2), 'truncated'),
])
def test_invalid_archives_rejected(tmp_path, payload, match):
    with pytest.raises(HuffmanFormatError, match=match):
        decompress_bytes(tmp_path, payload)


def test_empty_archive_decodes_to_empty_file(tmp_path):
    assert decompress_bytes(tmp_path, archive(b'')) == b''


def test_split_write_and_rem():
    whole, rest = split_write_and_rem(bitarray('1' * 19))
    assert len(whole) == 16 and rest == bitarray('111')


def test_header_validation_and_missing_codes():
    c = Compression(verbose=False)
    c.char_freq = {1: 1, 2: 1}
    with pytest.raises(HuffmanError, match='header is invalid'):
        c.validate_header(b'0')
    c.table_of_codes = {65: bitarray()}
    with pytest.raises(HuffmanError, match="symbol 65 doesn't have a code"):
        c.validate_table_of_codes()


def test_node():
    a, b = Node(freq=2, letter=1), Node(freq=3, letter=2)
    p = Node.parent(a, b)
    assert p.freq == 5 and not p.is_leaf and a.is_leaf


def test_verbose_output(tmp_path, capsys):
    src = tmp_path / 'src'
    src.write_bytes(b'hello hello')
    Compression().compress(str(src), str(tmp_path / 'c'))
    Decompression().decompress(str(tmp_path / 'c'), str(tmp_path / 'd'))
    out = capsys.readouterr().out
    assert 'different symbols' in out and 'Size of input file' in out
    assert 'seconds to compress file' in out and 'seconds to decompress' in out
    get_compression_info(str(src), str(tmp_path / 'c'))
    assert '--- Compression:' in capsys.readouterr().out


def test_compression_info_for_empty_source(tmp_path, capsys):
    (tmp_path / 'e').write_bytes(b'')
    get_compression_info(str(tmp_path / 'e'), str(tmp_path / 'e'))
    assert 'source file is empty' in capsys.readouterr().out
