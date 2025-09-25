import time
from collections.abc import Callable

import pytest


def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: float = 10,
    interval: float = 0.1,
    description: str = "condition",
) -> bool:
    """Wait for a condition to be met with exponential backoff for efficiency."""
    start = time.time()
    current_interval = interval
    max_interval = 1.0  # Cap backoff at 1 second

    while time.time() - start < timeout:
        if condition_func():
            return True
        time.sleep(current_interval)
        # Exponential backoff for efficiency
        current_interval = min(current_interval * 1.2, max_interval)

    pytest.fail(f"{description} was not met within {timeout} seconds")
