from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    import subprocess


class PowerShellRunnerPort(Protocol):
    def run_powershell_command(
        self, command: list[str], check: bool = True
    ) -> subprocess.CompletedProcess | None: ...
