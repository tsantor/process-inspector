from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class ServiceRuntimeState:
    process: Any | None = None
    pid: int | None = None
    last_seen: datetime | None = None
    last_running_state: bool | None = None

    def reset(self) -> None:
        self.process = None
        self.pid = None

    def mark_seen(self, now_utc: datetime) -> None:
        self.last_seen = now_utc
