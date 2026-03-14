from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class TaskInfoDTO:
    name: str
    status: str
    is_running: bool
    last_run_time: str | None
    last_run_result: str | None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "is_running": self.is_running,
            "last_run_time": self.last_run_time,
            "last_run_result": self.last_run_result,
        }
