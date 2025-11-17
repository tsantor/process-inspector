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
        self._pid: int | None = None
        self._process: psutil.Process | None = None
        self._last_seen: datetime | None = None
        self._last_running_state: bool | None = None

    def __str__(self) -> str:
        return f"'{self.name} (PID: {self._pid})"

    def _sync_process_cache(self) -> psutil.Process | None:
        """
        Synchronize cached PID and process with current state.
        Returns the current process or None if not running.
        """
        current_pid = self.get_pid()

        # PID hasn't changed, return cached process
        if current_pid == self._pid:
            return self._process

        # PID changed - update cache
        self._pid = current_pid

        if current_pid is None:
            self._process = None
            return None

        # Create new process object for new PID
        try:
            self._process = psutil.Process(current_pid)
            return self._process
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning("Failed to get process for %s: %s", self, e)
            self._process = None
            return None

    @abstractmethod
    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""

    def pid(self) -> int | None:
        """Get current PID (may be cached from recent check)."""
        self._sync_process_cache()
        return self._pid

    def get_process(self) -> psutil.Process | None:
        """Get current process object."""
        return self._sync_process_cache()

    def reset_cache(self):
        """Clear cached PID and process info."""
        self._process = None
        self._pid = None

    def is_running(self) -> bool:
        """Check if service is running."""
        current_process = self.get_process()

        if not current_process:
            self.reset_cache()
            self._update_running_state(is_running=False)
            return False

        running = self.status() in ["RUNNING", "SLEEPING"]
        if running:
            self._last_seen = datetime.now(tz=UTC)

        self._update_running_state(is_running=running)
        return running

    def _update_running_state(self, is_running: bool) -> None:
        """Track and notify on running state changes."""
        if self._last_running_state != is_running:
            logger.debug(
                "ServiceInterface: Service %s running state changed: %s",
                self.name,
                is_running,
            )
            if self._on_state_change_cb:
                self._on_state_change_cb(service=self, is_running=is_running)
            self._last_running_state = is_running

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

    def as_dict(self) -> dict:
        return {"name": self.name}

    def get_last_seen_str(self) -> str | None:
        """Return last seen datetime as string or None."""
        return self._last_seen.isoformat() if self._last_seen else None

    def process_info(self) -> dict:
        """Get detailed process information."""
        proc = self.get_process()

        if proc:
            try:
                return {
                    **get_process_info(proc),
                    "last_seen": self.get_last_seen_str(),
                }
            except psutil.NoSuchProcess:
                logger.warning("Process %s no longer exists.", self)
                self.reset_cache()
                self._update_running_state(is_running=False)

        return {
            "is_running": False,
            "last_seen": self.get_last_seen_str(),
        }
