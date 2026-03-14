from __future__ import annotations

from typing import Protocol


class TeamviewerControllerPort(Protocol):
    def is_running(self) -> bool: ...

    def open(self) -> bool: ...

    def close(self) -> bool: ...
