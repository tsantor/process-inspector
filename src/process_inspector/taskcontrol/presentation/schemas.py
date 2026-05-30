from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskSchema:
    name: str
    status: str
    is_running: bool
    last_run_time: str | None
    last_run_result: str | None
