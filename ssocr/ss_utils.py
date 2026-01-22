import time
from collections.abc import Callable
from typing import Any

from ss_log import log


def timer(name: str | None = None):
    def decorator(func: Callable):
        def wrapper(*args: Any, **kwargs: Any):
            start_time = time.time()
            func(*args, **kwargs)
            log.info(
                f"{'' if name is None else f'{name} '}耗时: {(time.time() - start_time):.3f}s"
            )

        return wrapper

    return decorator
