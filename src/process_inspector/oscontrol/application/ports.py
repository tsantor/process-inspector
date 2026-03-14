from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from process_inspector.oscontrol.domain.value_objects import RebootRequest


class CommandRunnerPort(Protocol):
    def run_command(self, request: RebootRequest) -> bool: ...
