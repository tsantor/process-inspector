from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any

import psutil

from process_inspector.utils.datetimeutils import human_datetime_short
from process_inspector.utils.processutils import get_process_by_name
from process_inspector.utils.processutils import get_process_info

if TYPE_CHECKING:
    from pathlib import Path


class PsutilRuntimeRepository:
    """Infrastructure adapter backed by psutil and existing utility helpers."""

    def find_process(self, app_path: Path) -> psutil.Process | None:
        return get_process_by_name(app_path)

    def load_process(self, pid: int) -> psutil.Process:
        return psutil.Process(pid)

    def is_process_running(self, process: psutil.Process) -> bool:
        return process.is_running()

    def process_status(self, process: psutil.Process) -> str:
        return process.status()

    def process_create_time(self, process: psutil.Process) -> float:
        return process.create_time()

    def terminate_process(self, process: psutil.Process) -> None:
        process.terminate()

    def kill_process(self, process: psutil.Process) -> None:
        process.kill()

    def wait_process(self, process: psutil.Process, timeout: float) -> None:
        process.wait(timeout=timeout)

    def get_process_info(self, process: psutil.Process) -> dict[str, Any]:
        return get_process_info(process)

    def human_datetime_short(self, value: datetime) -> str:
        return human_datetime_short(value)

    def now_utc(self) -> datetime:
        return datetime.now(tz=UTC)
