from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class AppRuntimeState:
    """Mutable runtime cache for the tracked application process."""

    process: Any | None = None
    pid: int | None = None
    create_time: float | None = None
    last_seen: datetime | None = None
    last_running_state: bool | None = None

    def reset(self) -> None:
        self.process = None
        self.pid = None
        self.create_time = None

    def mark_seen(self, now_utc: datetime) -> None:
        self.last_seen = now_utc
