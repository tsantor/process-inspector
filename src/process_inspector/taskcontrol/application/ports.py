from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from process_inspector.taskcontrol.application.dtos import CommandResult


class PowerShellRunnerPort(Protocol):
    def run_powershell_command(
        self, command: list[str], check: bool = True
    ) -> CommandResult | None: ...
