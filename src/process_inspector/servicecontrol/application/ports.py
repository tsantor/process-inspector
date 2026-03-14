from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    from datetime import datetime


class ServiceRuntimePort(Protocol):
    def load_process(self, pid: int) -> Any: ...

    def get_process_info(self, process: Any) -> dict[str, Any]: ...

    def now_utc(self) -> datetime: ...
