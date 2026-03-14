from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from process_inspector.servicecontrol.domain.entities import ServiceRuntimeState

if TYPE_CHECKING:
    from process_inspector.servicecontrol.application.ports import ServiceRuntimePort

logger = logging.getLogger(__name__)


class ServiceRuntimeService:
    def __init__(self, runtime_port: ServiceRuntimePort, state_change_callback=None):
        self._runtime_port = runtime_port
        self._state = ServiceRuntimeState()
        self._on_state_change_cb = state_change_callback

    @property
    def pid(self) -> int | None:
        return self._state.pid

    @property
    def process(self) -> Any | None:
        return self._state.process

    def reset_cache(self) -> None:
        self._state.reset()

    def update_running_state(self, service: Any, *, is_running: bool) -> None:
        if self._state.last_running_state != is_running:
            if self._on_state_change_cb:
                self._on_state_change_cb(service=service, is_running=is_running)
            self._state.last_running_state = is_running

    def sync_process_cache(
        self, service: Any, *, current_pid: int | None
    ) -> Any | None:
        if current_pid == self._state.pid:
            return self._state.process

        self._state.pid = current_pid

        if current_pid is None:
            self._state.process = None
            return None

        try:
            self._state.process = self._runtime_port.load_process(current_pid)
            return self._state.process
        except Exception as exc:
            if self._runtime_port.is_process_error(exc):
                logger.warning("Failed to get process for %s: %s", service, exc)
                self._state.process = None
                return None
            raise

    def evaluate_running(
        self,
        service: Any,
        *,
        process: Any | None,
        status_value: str,
    ) -> bool:
        if not process:
            self.reset_cache()
            self.update_running_state(service, is_running=False)
            return False

        running = status_value in ["RUNNING", "SLEEPING"]
        if running:
            self._state.mark_seen(self._runtime_port.now_utc())

        self.update_running_state(service, is_running=running)
        return running

    def get_last_seen_str(self) -> str | None:
        if self._state.last_seen is None:
            return None
        return self._state.last_seen.isoformat()

    def process_info(self, service: Any) -> dict:
        process = self._state.process
        if process:
            try:
                return {
                    **self._runtime_port.get_process_info(process),
                    "last_seen": self.get_last_seen_str(),
                }
            except Exception as exc:
                if self._runtime_port.is_process_error(exc):
                    logger.warning("Failed to get process for %s: %s", service, exc)
                    self.reset_cache()
                    self.update_running_state(service, is_running=False)
                else:
                    raise

        return {
            "is_running": False,
            "last_seen": self.get_last_seen_str(),
        }
