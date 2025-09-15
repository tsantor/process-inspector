import logging
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path

import psutil  # assuming you're using psutil under the hood

from process_inspector.utils.datetimeutils import human_datetime_short
from process_inspector.utils.processutils import get_process_by_name
from process_inspector.utils.processutils import get_process_info

logger = logging.getLogger(__name__)


class AppInterface(ABC):
    """Basic control of an App"""

    def __init__(self, app_path: Path):
        if not app_path.exists():
            logger.warning("App path does not exist: %s", app_path)  # pragma: no cover

        self.app_path = app_path
        self.app_exe = app_path.name
        self.app_name = app_path.stem
        self._pid = None
        self._process = None

    def is_installed(self) -> bool:
        return self.app_path.exists()

    @property
    def process(self):
        """Return cached process if running, else refresh."""
        if self._process is None or not self.is_running():
            logger.debug("Refreshing process info for %s", self.app_name)
            self._process = self._get_process()
            self._pid = self._process.pid if self._process else None
        return self._process

    def _get_process(self):
        """Find the process by name/path if PID not usable."""
        return get_process_by_name(self.app_path)

    def _get_process_by_pid(self):
        """Check if cached PID is alive and matches expected exe."""
        if self._pid is None:
            return None
        try:
            proc = psutil.Process(self._pid)
            if proc.is_running() and proc.name() == self.app_exe:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        return None

    @abstractmethod
    def is_running(self) -> bool: ...

    @abstractmethod
    def open(self) -> bool: ...

    @abstractmethod
    def close(self) -> bool: ...

    @abstractmethod
    def get_version(self) -> str: ...

    def get_install_date(self) -> datetime:
        tz = datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(self.app_path.stat().st_mtime, tz=tz)

    def to_dict(self) -> dict:
        return {
            "exe": self.app_exe,
            "name": self.app_name,
            "path": str(self.app_path),
            "is_installed": self.is_installed(),
            "version": self.get_version(),
            "install_date_short": self.get_install_date().strftime("%Y-%m-%d"),
            "install_date": human_datetime_short(self.get_install_date()),
        }

    @cached_property
    def as_dict(self) -> dict:
        return self.to_dict()

    def process_info(self) -> dict:
        if proc := self.process:
            return get_process_info(proc)
        return {}
