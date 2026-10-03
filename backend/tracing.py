import time


def start_timer():
    return time.perf_counter()


def elapsed(start: float) -> float:
    return time.perf_counter() - start
