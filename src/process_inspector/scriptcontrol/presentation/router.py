from __future__ import annotations

from abc import abstractmethod

from process_inspector.appcontrol.infrastructure.base import AppBase
from process_inspector.scriptcontrol.presentation.dependencies import (
    get_script_execution_service,
)


class ScriptInterface(AppBase):
    """Basic control of a Script which launches a child process."""

    def __init__(self, app_path, state_change_callback=None):
        super().__init__(app_path, state_change_callback)
        self._script_service = get_script_execution_service()

    def open(self) -> bool:
        return self._script_service.run(
            self,
            run_callable=self.get_script_result,
            set_running_state=self._update_running_state,
        )

    def run(self) -> bool:
        return self.open()

    def get_version(self) -> str:
        return "--"

    @abstractmethod
    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
