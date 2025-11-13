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
        self._process: psutil.Process = None
        self._pid: int = None
        self._last_seen: datetime = None
        self._last_running_state: bool | None = None

        # Initialize PID and process (if already running)
        # self.is_running()

        # current_pid = self.get_pid()
        # if current_pid:
        #     self._pid = current_pid
        #     self._process = self._get_process_for_pid(current_pid)

        # logger.info("Service: %s | Status: %s", name, self.status())

    def __str__(self) -> str:
        return f"'{self.name} (PID: {self._pid})"

    def reset_cache(self):
        """Clear cached PID and process info."""
        # logger.debug("Resetting cache for app: %s (PID: %s)", self.app_name, self._pid)
        self._process = None
        self._pid = None

    @abstractmethod
    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""

    def pid(self) -> int | None:
        """Get current PID, updating cache if it changed."""
        current_pid = self.get_pid()

        # Update cache if PID changed
        if current_pid != self._pid:
            self._pid = current_pid
            if current_pid:
                self._process = self._get_process_for_pid(current_pid)
            else:
                self._pid = None
                self._process = None

        return self._pid

    def get_process(self) -> psutil.Process | None:
        """Get process object, fetching only if PID changed."""
        # Ensure PID is up to date (this will update cache if needed)
        current_pid = self.pid()

        if not current_pid:
            return None

        return self._process

    def _get_process_for_pid(self, pid: int) -> psutil.Process | None:
        """Helper to safely create Process object."""
        try:
            return psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning("Failed to get process %s: %s", self, e)
            return None

    def is_running(self) -> bool:
        """Check if service is running."""
        # logger.debug("Checking if service '%s' is running", self.name)
        # This will refresh PID/process if needed
        current_process = self.get_process()

        if not current_process:
            # logger.debug("No process found for service '%s'", self.name)
            self.reset_cache()
            self._update_running_state(is_running=False)
            return False

        running = self.status() in ["RUNNING", "SLEEPING"]
        if running:
            # logger.debug(
            #     "Service '%s' is running with PID %s", self.name, current_process.pid
            # )
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
            # if self._last_running_state is not None:  # Skip first check
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

    def __repr__(self):
        return f"Service('{self.name}')"

    def get_last_seen_str(self) -> str | None:
        """Return last seen datetime as string or None."""
        if self._last_seen is None:
            return None
        return self._last_seen.isoformat()

    # @cached_property
    # def _cached_dict(self) -> dict:
    #     return {
    #         "name": self.name,
    #         # "path": str(self.app_path),
    #         # "is_installed": self.is_installed(),
    #         # "version": self.version,
    #         # "install_date_short": self.install_date_short,
    #         # "install_date": self.install_date_human_short,
    #     }

    # def as_dict(self) -> dict:
    #     """We want to preserve this method for backward compatibility."""
    #     return self._cached_dict

    def as_dict(self) -> dict:
        # NOTE: We include the pid, is_running, and status here for services
        # but we don't do that for apps. Why?
        return {
            "name": self.name,
            # Non-standard fields for services
            # "pid": self.pid(),
            # "is_running": self.is_running(),
            # "status": self.status(),
        }

    def process_info(self) -> dict:
        if proc := self._process:
            try:
                return {
                    **get_process_info(proc),
                    # We override these fields to use values from supervisorctl
                    # "pid": self.pid(),
                    # "is_running": self.is_running(),
                    # "status": self.status(),
                    "last_seen": self.get_last_seen_str(),
                }
            except psutil.NoSuchProcess:
                logger.warning("Process %s no longer exists.", self)
                self.reset_cache()
                self._update_running_state(is_running=False)
        logger.warning("No process info available for %s.", self)
        # We can reach here if the process was killed by the user
        return {
            "is_running": False,
            "last_seen": self.get_last_seen_str(),
        }
