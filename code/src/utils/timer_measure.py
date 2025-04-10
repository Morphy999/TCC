import re
import time
from functools import wraps


def snake2camelback(name):
    return re.sub(r"_([a-z])", lambda x: x.group(1).upper(), name)


def timer_measure(func):
    @wraps(func)
    def timer_measure_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        func_name = snake2camelback(func.__name__)
        print(f'{{"{func_name}Time": {total_time:.4f}}}')
        return result

    return timer_measure_wrapper
