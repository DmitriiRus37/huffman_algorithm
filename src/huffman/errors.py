class HuffmanError(Exception):
    """Base class for errors raised by the huffman package."""


class HuffmanFormatError(HuffmanError, ValueError):
    """The compressed file is not a valid Huffman archive (foreign, truncated or corrupted)."""
