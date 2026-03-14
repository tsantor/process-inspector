from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import Any

import psutil

from process_inspector.utils.processutils import get_process_info


class PsutilServiceRuntimeRepository:
    def load_process(self, pid: int) -> psutil.Process:
        return psutil.Process(pid)

    def get_process_info(self, process: psutil.Process) -> dict[str, Any]:
        return get_process_info(process)

    def now_utc(self) -> datetime:
        return datetime.now(tz=UTC)
