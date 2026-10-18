import functools
import os
import time
from tqdm import tqdm


def print_time_spent(message):
    """Print how long the method took; methods of objects with verbose=False stay silent."""
    def calculate_time(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            result = func(self, *args, **kwargs)
            if self.verbose:
                print(f"--- {round(time.time() - start_time, 3)} seconds {message} ---")
            return result
        return wrapper
    return calculate_time


def get_compression_info(s, d) -> None:
    input_size = os.path.getsize(s)
    output_size = os.path.getsize(d)
    if input_size == 0:
        print("--- Compression: source file is empty ---")
        return
    compress_percent = "{:.2f}".format(output_size / input_size * 100)
    print(f"--- Compression: {compress_percent} % ---")


def update_pbar(val: float, pbar: tqdm) -> None:
    pbar.update(val)
