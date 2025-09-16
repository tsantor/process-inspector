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

        self._pid = None
        self._process = None

        # Initialize PID and process (if already running)
        self.is_running()

    @property
    def process(self) -> psutil.Process | None:
        """Return cached process if running, else refresh."""
        if self._process is None or not self.is_running():
            # logger.debug("Refreshing process info for %s", self.app_name)
            self._process = get_process_by_name(self.app_path)
            self._pid = self._process.pid if self._process else None
        return self._process

    def is_installed(self) -> bool:
        return self.app_path.exists()

    @abstractmethod
    def is_running(self) -> bool: ...

    @abstractmethod
    def open(self) -> bool: ...

    @abstractmethod
    def close(self) -> bool: ...

    @abstractmethod
    def get_version(self) -> str: ...

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

    def to_dict(self) -> dict:
        return {
            "exe": self.app_exe,
            "name": self.app_name,
            "path": str(self.app_path),
            "is_installed": self.is_installed(),
            "version": self.get_version(),
            "install_date_short": self.install_date_short,
            "install_date": self.install_date_human_short,
        }

    @cached_property
    def as_dict(self) -> dict:
        return self.to_dict()

    def process_info(self) -> dict:
        if proc := self.process:
            return get_process_info(proc)
        return {}
