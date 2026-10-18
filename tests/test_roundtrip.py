import shutil
from pathlib import Path
import pytest

import main
from huffman import Decompression, HuffmanFormatError

TEST_FILES = Path(__file__).parent / 'test_files'


def compress(source: Path, dest: Path) -> None:
    assert main.main(['compress', '--quiet', str(source), str(dest)]) == 0


def decompress(source: Path, dest: Path) -> None:
    assert main.main(['decompress', '--quiet', str(source), str(dest)]) == 0


def assert_round_trip(original: Path, tmp_path: Path) -> None:
    compressed = tmp_path / (original.name + '.huff')
    decompressed = tmp_path / (original.name + '.res')
    compress(original, compressed)
    decompress(compressed, decompressed)
    assert decompressed.read_bytes() == original.read_bytes()


def round_trip_bytes(data: bytes, tmp_path: Path) -> None:
    original = tmp_path / 'source'
    original.write_bytes(data)
    assert_round_trip(original, tmp_path)


@pytest.mark.parametrize('file_name', ['test1.txt', 'test2.xml', 'test3.txt', 'test4.txt', 'test6.txt'])
def test_sample_files(file_name, tmp_path):
    assert_round_trip(TEST_FILES / file_name, tmp_path)


@pytest.mark.slow
def test_large_file(tmp_path):
    original = tmp_path / 'test5.xml'
    with open(original, 'wb') as f_out:
        for _ in range(5):
            with open(TEST_FILES / 'test2.xml', 'rb') as f_in:
                shutil.copyfileobj(f_in, f_out)
    assert_round_trip(original, tmp_path)


@pytest.mark.parametrize('data', [
    pytest.param(b'', id='empty'),
    pytest.param(b'a', id='one-byte'),
    pytest.param(b'z' * 100_000, id='single-symbol'),
    pytest.param(b'ab' * 1000, id='two-symbols'),
    pytest.param(b'first line\r\nsecond line\r\n\r\nlast\r', id='crlf'),
    pytest.param(b'caf\xc3\xa9 \xff\xfe\x00\x01 binary \x80\x81' * 100, id='non-utf8'),
    pytest.param(bytes(range(256)) * 300, id='all-byte-values'),
    pytest.param(bytes(range(256)), id='all-byte-values-once'),
])
def test_edge_cases(data, tmp_path):
    round_trip_bytes(data, tmp_path)


def test_existing_destination_is_overwritten(tmp_path):
    original = tmp_path / 'source'
    original.write_bytes(b'hello world')
    compressed = tmp_path / 'source.huff'
    decompressed = tmp_path / 'source.res'
    decompressed.write_bytes(b'stale content that is longer than the result')
    compress(original, compressed)
    decompress(compressed, decompressed)
    assert decompressed.read_bytes() == b'hello world'


CORRUPTIONS = {
    'bad magic': lambda archive: b'XXXX' + archive[4:],
    'truncated': lambda archive: archive[:-10],
    'flipped data byte': lambda archive: archive[:-5] + bytes([archive[-5] ^ 0xff]) + archive[-4:],
    'trailing garbage': lambda archive: archive + b'\x00\x00',
}


@pytest.mark.parametrize('corruption', CORRUPTIONS.keys())
def test_corrupted_archive_is_rejected(corruption, tmp_path):
    original = tmp_path / 'source'
    original.write_bytes(b'some text to compress, ' * 1000)
    compressed = tmp_path / 'source.huff'
    compress(original, compressed)
    compressed.write_bytes(CORRUPTIONS[corruption](compressed.read_bytes()))
    with pytest.raises(HuffmanFormatError):
        Decompression(verbose=False).decompress(str(compressed), str(tmp_path / 'source.res'))
    assert main.main(['decompress', '-q', str(compressed), str(tmp_path / 'source.res')]) == 1


def test_legacy_cli_arguments(tmp_path):
    original = tmp_path / 'source'
    original.write_bytes(b'legacy command line')
    compressed = tmp_path / 'source.huff'
    decompressed = tmp_path / 'source.res'
    assert main.main([str(original), str(compressed)]) == 0
    assert main.main(['decode', str(compressed), str(decompressed)]) == 0
    assert decompressed.read_bytes() == original.read_bytes()


def test_cli_usage_errors(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main.main([])
    assert exc.value.code == 2
    assert main.main(['compress', '-q', str(tmp_path / 'missing'), str(tmp_path / 'out')]) == 1
    assert 'error:' in capsys.readouterr().err
