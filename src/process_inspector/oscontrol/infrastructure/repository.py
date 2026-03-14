from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from process_inspector.oscontrol.application.ports import CommandRunnerPort

if TYPE_CHECKING:
    from process_inspector.oscontrol.domain.value_objects import RebootRequest


class SubprocessCommandRunner(CommandRunnerPort):
    def run_command(self, request: RebootRequest) -> bool:
        proc = subprocess.run(  # noqa: S603
            list(request.command), check=True, capture_output=True
        )
        return proc.returncode == 0
