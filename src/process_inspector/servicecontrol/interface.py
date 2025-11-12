import logging
from abc import ABC
from abc import abstractmethod
from datetime import UTC
from datetime import datetime

import psutil

from process_inspector.utils.processutils import get_process_info

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """Basic control of a Service"""

    def __init__(self, name, state_change_callback=None):
        self.name: str = name
        self._on_state_change_cb = state_change_callback
        self._cached_pid: int = None
        self._cached_process: psutil.Process = None
        self._last_seen: datetime = None

    def __str__(self) -> str:
        return f"'{self.name} (PID: {self._cached_pid})"

    def reset_cache(self):
        """Clear cached PID and process info."""
        self._cached_pid = None
        self._cached_process = None

    @abstractmethod
    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""

    def pid(self) -> int | None:
        """Get current PID, updating cache if it changed."""
        current_pid = self.get_pid()

        # Update cache if PID changed
        if current_pid != self._cached_pid:
            self._cached_pid = current_pid
            if current_pid:
                self._cached_process = self._get_process_for_pid(current_pid)
            else:
                self._cached_process = None

        return self._cached_pid

    def get_process(self) -> psutil.Process | None:
        """Get process object, fetching only if PID changed."""
        # Ensure PID is up to date (this will update cache if needed)
        current_pid = self.pid()

        if not current_pid:
            return None

        return self._cached_process

    def _get_process_for_pid(self, pid: int) -> psutil.Process | None:
        """Helper to safely create Process object."""
        try:
            return psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning("Failed to get process %s: %s", self, e)
            return None

    def is_running(self) -> bool:
        """Check if service is running."""
        # This will refresh PID/process if needed
        current_process = self.get_process()

        if not current_process:
            # logger.debug("No process found for service '%s'", self.name)
            self.reset_cache()
            return False

        running = self.status() in ["RUNNING", "SLEEPING"]
        if running:
            self._last_seen = datetime.now(tz=UTC)
        return running

    @abstractmethod
    def start(self) -> bool:
        """Start service"""

    @abstractmethod
    def stop(self) -> bool:
        """Stop service"""

    @abstractmethod
    def restart(self) -> bool:
        """Restart service"""

    @abstractmethod
    def status(self) -> str:
        """Service status"""

    def open(self) -> bool:
        """Alias so we can use a service like an app."""
        return self.start()  # pragma: no cover

    def close(self) -> bool:
        """Alias so we can use a service like an app."""
        return self.stop()  # pragma: no cover

    def __repr__(self):
        return f"Service('{self.name}')"

    def as_dict(self) -> dict:
        return {
            "pid": self.pid(),
            "name": self.name,
            "is_running": self.is_running(),
            "status": self.status(),
            "last_seen": self._last_seen.isoformat() if self._last_seen else None,
        }

    def process_info(self) -> dict:
        if proc := self._cached_process:
            try:
                return get_process_info(proc)
            except psutil.NoSuchProcess:
                self.reset_cache()
        return {}
