import logging
from abc import ABC
from abc import abstractmethod
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

    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.app_exe = app_path.name
        self.app_name = app_path.stem

        if not self.is_installed():
            logger.warning(
                "App path does not exist: '%s'", app_path
            )  # pragma: no cover

        self._process: psutil.Process | None = None
        self._pid: int | None = None
        self._create_time: float | None = None

        # Initialize PID and process (if already running)
        self.is_running()

    def reset_cache(self) -> None:
        self._process = None
        self._pid = None
        self._create_time = None

    def is_installed(self) -> bool:
        return self.app_path.exists()

    def is_running(self) -> bool:
        """Check if the *specific* app instance is running."""
        if self._pid is None:
            # Fallback: check if the app is running (first run or manual restart)
            proc = get_process_by_name(self.app_path, newest=True)
            if not proc:
                self.reset_cache()
                return False

            # Found a running instance, adopt it
            logger.debug("Found running process: %s (PID: %s)", proc.name(), proc.pid)
            self._process = proc
            self._pid = proc.pid
            try:
                self._create_time = proc.create_time()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.reset_cache()
                return False

        try:
            # Use cached process or look it up again
            p = self._process or psutil.Process(self._pid)
            if abs(p.create_time() - self._create_time) > PID_CREATE_TIME_TOLERANCE:
                self.reset_cache()
                return False

            # Check status
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            self.reset_cache()
            return False

    @abstractmethod
    def open(self) -> bool: ...

    def close(self) -> bool:
        """Close the running app we launched (terminate -> kill) and wait."""
        if not self.is_running():
            self.reset_cache()
            return True

        try:
            p = self._process or psutil.Process(self._pid)
        except psutil.NoSuchProcess:
            self.reset_cache()
            return True

        # Try graceful terminate (SIGTERM), then escalate (SIGKILL)
        try:
            p.terminate()
            p.wait(timeout=2)
            logger.debug("Terminated process: %s (PID: %s)", self.app_name, self._pid)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                p.kill()
                p.wait(timeout=3)
                logger.debug("Killed process: %s (PID: %s)", self.app_name, self._pid)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning(
                    "Failed to kill process: %s (PID: %s)", self.app_name, self._pid
                )

        self.reset_cache()
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

    def process_info(self) -> dict:
        """Safely return process info dict or empty dict."""
        if proc := self._process:
            try:
                return get_process_info(proc)
            except psutil.NoSuchProcess:
                logger.warning(
                    "Process for app '%s' with PID %s no longer exists.",
                    self.app_name,
                    self._pid,
                )
                self.reset_cache()
        # We can reach here if the process was killed by the user
        return {"is_running": False}
