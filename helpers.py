import os
import time


def print_time_spent(message):
    def calculate_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            print(f"--- {time.time() - start_time} seconds {message} ---")
            return result
        return wrapper
    return calculate_time


def get_compression_info(s, d):
    input_size = os.path.getsize(s)
    output_size = os.path.getsize(d)
    compress_percent = "{:.2f}".format(output_size / input_size * 100)
    print(f"--- Compression: {compress_percent} % ---")