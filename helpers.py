import time


def print_time_spent(message):
    def calculate_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            print(f"--- {time.time() - start_time} seconds to {message} ---")
            return result
        return wrapper
    return calculate_time
