from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from process_inspector.oscontrol.domain.value_objects import RebootRequest


class CommandRunnerPort:
    def run_command(self, request: RebootRequest) -> bool:
        raise NotImplementedError
