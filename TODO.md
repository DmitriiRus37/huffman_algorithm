# TODO — huffman_algorithm enhancements

Findings from a review on 2026-10-18. Ordered by priority.

## P0 — Correctness

- [x] **Work on bytes, not text.** Compression and decompression open files in text mode,
  so the round trip is not lossless:
  - CRLF line endings come back as LF (verified: `ab\r\ncd\r\n` does not round-trip).
  - Non-UTF-8 / binary input crashes with `UnicodeDecodeError` (verified).
  - `encode_and_write` opens the source without `encoding=` (`src/compression.py:70`), and so does
    `decompress` for the output (`src/decompression.py:36`), so behaviour depends on the platform locale.
  - Fix: read with `'rb'`, count byte frequencies (alphabet is at most 256), write the output with `'wb'`.
    The header can then store raw bytes instead of UTF-8 characters.
- [x] **Handle empty files.** Compressing an empty file currently raises `Exception("Source file is empty")`.
  Write a valid, empty archive and make it decompress to an empty file.
- [x] **Fix the round-trip check in the tests.** `tests/tests.py:30` compares with `zip()`, which stops at the
  shorter file, so a truncated output still passes. Compare the whole file contents (`filecmp.cmp(..., shallow=False)`
  or the bytes directly).

## P1 — Robustness & performance

- [x] **Write the header first; drop the temp file.** The tree is known before encoding, so write the header and a
  placeholder padding byte, encode, then `seek()` back and patch the padding byte. This removes the full second copy
  of the output and the hard-coded `tmp` file in the CWD (`src/compression.py:88-98`), which collides when two runs
  happen at once.
- [x] **Speed up block decoding.** `get_symbols` (`src/decompression.py:100-120`) decodes the whole 64 KB block again
  for each trimmed bit until it succeeds. Decompression is about 2.5× slower than compression (5.6 s vs 2.1 s on
  `test2.xml`). Options: walk the tree once to find the last complete code boundary, or store the symbol count in
  the header and decode only that many symbols.
- [x] **Chunk encoding by size, not by line.** `encode_file` iterates with `for line in file`
  (`src/compression.py:103`), so a file with one huge line is loaded into memory all at once. Read fixed-size chunks
  instead (this also falls out of the switch to bytes).
- [x] **Stop slicing the header string in `restore_tree`.** `symbol_str.val[1:]` makes it O(n²)
  (`src/decompression.py:64-75`). Use an index or iterator.
- [x] **Add a file-format magic number and version** so that non-Huffman files are rejected with a clear error.
  Optionally add a CRC32 of the original data.

## P2 — Tooling, tests & CI

- [ ] **Fix CI.** `.github/workflows/python-app.yml` uses Python 3.10 and installs from `requirements.txt`, which
  doesn't exist (the project uses Pipfile). As a result, `bitarray` and `tqdm` are never installed. Align it with the
  Pipfile, bump `actions/checkout` and `actions/setup-python` to current versions, and run pytest from the right directory.
- [ ] **Make tests independent of the CWD.** Paths such as `'test_files/test1.txt'` only work when run from `tests/`.
  Use `pathlib.Path(__file__).parent` or pytest's `tmp_path`, and don't write `test5.xml` into `test_files/`.
- [ ] **Add edge-case tests:** empty file, single-symbol file, CRLF, binary/non-UTF-8, and a file where every byte
  value appears.
- [ ] **Make the large-file test cheaper.** The 15 MB `test2.xml` in the repo is the main cause of the ~130 s test run.
  Generate the large input during the test, or mark it as `slow`.
- [ ] **Remove the unused `bitstring` dependency** from the Pipfile. Nothing imports it.
- [ ] **Package layout.** `src/` modules import each other as top-level modules (`from helpers import ...`), while
  tests import `from src import main`. Turn the code into a proper package (with `pyproject.toml`) so that imports
  work everywhere.

## P3 — Code quality / UX

- [ ] **Use `argparse` in `main.py`.** It should print usage and errors cleanly instead of raising `IndexError` when
  arguments are missing. Consider subcommands such as `compress` and `decompress`.
- [ ] **Replace the kwargs-dispatch `Node.__init__`** (`src/node.py`) with a `@dataclass` and an `is_leaf` property.
  Also replace the obscure `node.left == node.right is None` checks.
- [ ] **Raise specific exceptions** (`ValueError` or a custom `HuffmanFormatError`) instead of bare `Exception`.
- [ ] **Replace `WrapValue`** with return values. It exists only to fake out-parameters.
- [ ] **Reduce side effects in the library.** Progress bars and timing prints belong to the CLI and GUI layers.
  Add a `verbose`/`progress` flag.
- [ ] **Resolve `TODO` in `main.py:9`:** support archiving multiple files, or remove the comment.
