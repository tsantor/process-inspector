import logging
from abc import ABC
from abc import abstractmethod

import psutil

from process_inspector.utils.processutils import get_process_info

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """Basic control of a Service"""

    def __init__(self, name):
        self.name: str = name
        self._cached_pid: int = None
        self._cached_process: psutil.Process = None

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
            logger.warning("Failed to get process for PID %d: %s", pid, e)
            return None

    def is_running(self) -> bool:
        """Check if service is running."""
        # This will refresh PID/process if needed
        current_process = self.get_process()

        if not current_process:
            logger.debug("No process found for service '%s'", self.name)
            return False

        return self.status() in ["RUNNING", "SLEEPING"]

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
        }

    def process_info(self) -> dict:
        if proc := self._cached_process:
            try:
                return get_process_info(proc)
            except psutil.NoSuchProcess:
                self.reset_cache()
        return {}
