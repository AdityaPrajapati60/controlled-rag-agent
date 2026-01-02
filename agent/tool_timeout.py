# agent/tool_timeout.py

import threading
from contextlib import contextmanager


class ToolTimeout(Exception):
    pass


@contextmanager
def time_limit(seconds: int):
    timer = threading.Timer(seconds, lambda: (_ for _ in ()).throw(ToolTimeout()))
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
