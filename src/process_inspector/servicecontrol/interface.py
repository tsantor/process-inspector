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

        logger.info("Service: %s | Status: %s", name, self.status())

    def reset_cache(self):
        """Clear cached PID and process info."""
        self._cached_pid = None
        self._cached_process = None

    @abstractmethod
    def pid(self) -> int | None:
        """Get current PID, updating cache if it changed."""

    def get_process(self) -> psutil.Process | None:
        """Get process object, fetching only if PID changed."""
        # Ensure PID is up to date (this will update cache if needed)
        current_pid = self.pid()

        if not current_pid:
            return None

        return self._cached_process

    @abstractmethod
    def is_running(self) -> bool:
        """Determine if service is running"""

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
        return self.start()

    def close(self) -> bool:
        """Alias so we can use a service like an app."""
        return self.stop()

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
            return get_process_info(proc)
        return {}
