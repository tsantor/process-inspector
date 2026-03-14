from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from process_inspector.servicecontrol.application.dtos import ServiceInfoDTO
from process_inspector.servicecontrol.domain.value_objects import ServiceIdentity
from process_inspector.servicecontrol.infrastructure.factory import (
    build_runtime_service,
)


class ServiceControllerBase(ABC):
    """Shared service controller behavior used by concrete infrastructure implementations."""

    def __init__(self, name, state_change_callback=None):
        self._identity = ServiceIdentity(name=name)
        self.name = self._identity.name
        self._runtime = build_runtime_service(
            state_change_callback=state_change_callback
        )

    def __str__(self) -> str:
        return f"'{self.name} (PID: {self._runtime.pid})"

    def _sync_process_cache(self):
        return self._runtime.sync_process_cache(self, current_pid=self.get_pid())

    @abstractmethod
    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""

    def pid(self) -> int | None:
        self._sync_process_cache()
        return self._runtime.pid

    def get_process(self):
        return self._sync_process_cache()

    def reset_cache(self):
        self._runtime.reset_cache()

    def is_running(self) -> bool:
        return self._runtime.evaluate_running(
            self,
            process=self.get_process(),
            status_value=self.status(),
        )

    def _update_running_state(self, is_running: bool) -> None:
        self._runtime.update_running_state(self, is_running=is_running)

    @abstractmethod
    def start(self) -> bool:
        """Start service."""

    @abstractmethod
    def stop(self) -> bool:
        """Stop service."""

    @abstractmethod
    def restart(self) -> bool:
        """Restart service."""

    @abstractmethod
    def status(self) -> str:
        """Service status."""

    def open(self) -> bool:
        return self.start()  # pragma: no cover

    def close(self) -> bool:
        return self.stop()  # pragma: no cover

    def as_dict(self) -> dict:
        return ServiceInfoDTO(name=self.name).as_dict()

    def get_last_seen_str(self) -> str | None:
        return self._runtime.get_last_seen_str()

    def process_info(self) -> dict:
        self._sync_process_cache()
        return self._runtime.process_info(self)
