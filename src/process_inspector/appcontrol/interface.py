import logging
import time
from abc import ABC
from abc import abstractmethod
from datetime import UTC
from datetime import datetime
from functools import cached_property
from pathlib import Path

import psutil

from process_inspector.utils.datetimeutils import human_datetime_short
from process_inspector.utils.processutils import get_process_by_name
from process_inspector.utils.processutils import get_process_info

logger = logging.getLogger(__name__)

PID_CREATE_TIME_TOLERANCE = 0.001


class AppInterface(ABC):
    """Basic control of an App"""

    def __init__(self, app_path: Path, state_change_callback=None):
        self.app_path = app_path
        self.app_exe = app_path.name
        self.app_name = app_path.stem
        self._on_state_change_cb = state_change_callback

        if not self.is_installed():
            logger.warning(
                "App path does not exist: '%s'", app_path
            )  # pragma: no cover

        self._process: psutil.Process | None = None
        self._pid: int | None = None
        self._create_time: float | None = None
        self._last_seen: datetime | None = None
        self._last_running_state: bool | None = None

        # Initialize PID and process (if already running)
        self.is_running()

    def __str__(self) -> str:
        return f"'{self.app_name} (PID: {self._pid})"

    def reset_cache(self) -> None:
        """Clear cached PID and process info."""
        self._process = None
        self._pid = None
        self._create_time = None

    @property
    def pid(self) -> int | None:
        """Return the PID of the running app"""
        return self._pid

    def is_installed(self) -> bool:
        return self.app_path.exists()

    def is_running(self) -> bool:
        """Check if the *specific* app instance is running."""
        try:
            # If we don't have a process yet, try to find one
            if self._process is None:
                if self._pid is None:
                    # First run: find the process by name
                    proc = get_process_by_name(self.app_path, newest=True)
                    if not proc:
                        self._update_running_state(is_running=False)
                        return False
                else:
                    # We have a PID but no process object, recreate it
                    proc = psutil.Process(self._pid)

                # Cache the process and its metadata
                self._process = proc
                self._pid = proc.pid
                self._create_time = proc.create_time()

            # Now verify the cached process is still valid
            if (
                not self._process.is_running()
                or self._process.status() == psutil.STATUS_ZOMBIE
                or abs(self._process.create_time() - self._create_time)
                > PID_CREATE_TIME_TOLERANCE
            ):
                logger.debug("Process %s no longer valid. Resetting cache.", self)
                self.reset_cache()
                self._update_running_state(is_running=False)
                return False

            self._last_seen = datetime.now(tz=UTC)
            self._update_running_state(is_running=True)
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.debug("Process %s error", self)
            self.reset_cache()
            self._update_running_state(is_running=False)
            return False

    def _update_running_state(self, is_running: bool) -> None:
        """Track and notify on running state changes."""
        if self._last_running_state != is_running:
            if self._on_state_change_cb:
                self._on_state_change_cb(app=self, is_running=is_running)
            self._last_running_state = is_running

    @abstractmethod
    def open(self) -> bool:
        """Open app"""

    def close(self, timeout: float = 3.0) -> bool:
        """Close app"""
        if not self.is_running():
            self.reset_cache()
            self._update_running_state(is_running=False)
            return True

        start_time = time.perf_counter()

        try:
            p = self._process or psutil.Process(self._pid)
        except psutil.NoSuchProcess:
            self.reset_cache()
            self._update_running_state(is_running=False)
            return True

        # Try graceful terminate (SIGTERM), then escalate (SIGKILL)
        try:
            p.terminate()
            p.wait(timeout=5)
            logger.debug("Terminated process %s", self)
        except psutil.TimeoutExpired:
            try:
                p.kill()
                p.wait(timeout=3)
                logger.debug("Killed process %s", self)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning("Failed to kill process %s", self)
        except psutil.NoSuchProcess:
            logger.debug("Process %s already exited during termination", self)

        # Wait a moment for the quit to complete
        while self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning("Timed out waiting for %s to stop", self)
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "App '%s' quit successfully in %.3f seconds.",
            self.app_name,
            elapsed,
        )
        self.reset_cache()
        self._update_running_state(is_running=False)
        return True

    @abstractmethod
    def get_version(self) -> str: ...

    @cached_property
    def version(self) -> str:
        return self.get_version()

    @cached_property
    def install_date(self) -> datetime | None:
        """Return creation/install date of the application."""
        if self.is_installed() is False:
            return None
        tz = datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(self.app_path.stat().st_mtime, tz=tz)

    @cached_property
    def install_date_short(self) -> str | None:
        """Return short creation/install date of the application."""
        if self.install_date is None:
            return None
        return self.install_date.strftime("%Y-%m-%d")

    @cached_property
    def install_date_human_short(self) -> str | None:
        """Return human readable creation/install date of the application."""
        if self.install_date is None:
            return None
        return human_datetime_short(self.install_date)

    @cached_property
    def _cached_dict(self) -> dict:
        return {
            "exe": self.app_exe,
            "name": self.app_name,
            "path": str(self.app_path),
            "is_installed": self.is_installed(),
            "version": self.version,
            "install_date_short": self.install_date_short,
            "install_date": self.install_date_human_short,
        }

    def as_dict(self) -> dict:
        """We want to preserve this method for backward compatibility."""
        return self._cached_dict

    def get_last_seen_str(self) -> str | None:
        """Return last seen datetime as string or None."""
        if self._last_seen is None:
            return None
        return self._last_seen.isoformat()

    def process_info(self) -> dict:
        if proc := self._process:
            try:
                return {
                    **get_process_info(proc),
                    "last_seen": self.get_last_seen_str(),
                }
            except psutil.NoSuchProcess:
                logger.warning("Process %s no longer exists.", self)
                self.reset_cache()
                self._update_running_state(is_running=False)
        # logger.warning("No process info available for app %s.", self)
        # We can reach here if the process was killed by the user
        return {
            "is_running": False,
            "last_seen": self.get_last_seen_str(),
        }
