from __future__ import annotations

from typing import TYPE_CHECKING

from process_inspector.oscontrol.domain.entities import RebootResult
from process_inspector.oscontrol.domain.value_objects import RebootRequest

if TYPE_CHECKING:
    from process_inspector.oscontrol.application.ports import CommandRunnerPort


class RebootService:
    def __init__(self, command_runner: CommandRunnerPort):
        self._command_runner = command_runner

    def reboot(self, command: list[str]) -> bool:
        request = RebootRequest(command=tuple(command))
        result = RebootResult(succeeded=self._command_runner.run_command(request))
        return result.succeeded
