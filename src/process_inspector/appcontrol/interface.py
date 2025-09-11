import logging
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from pathlib import Path

from psutil import Process

from process_inspector.utils.datetimeutils import human_datetime_short
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

        # logger.info("App path: %s", app_path)
        # logger.info(self.to_dict())

    def is_installed(self) -> bool:
        """Determine if the app is installed."""
        return self.app_path.exists()

    @abstractmethod
    def get_process(self) -> Process:
        """Return the process object of the app."""

    @abstractmethod
    def is_running(self) -> bool:
        """Determine if app is running."""

    @abstractmethod
    def open(self) -> bool:
        """Open the app."""

    @abstractmethod
    def close(self) -> bool:
        """Close the app."""

    @abstractmethod
    def get_version(self) -> str:
        """Get the application's version."""

    def get_install_date(self) -> datetime:
        """Get the application's install date."""
        tz = datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(self.app_path.stat().st_mtime, tz=tz)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the object."""
        return {
            "exe": self.app_exe,
            "name": self.app_name,
            "path": str(self.app_path),
            "is_installed": self.is_installed(),
            "version": self.get_version(),
            "install_date_short": self.get_install_date().strftime("%Y-%m-%d"),
            "install_date": human_datetime_short(self.get_install_date()),
        }

    def process_info(self) -> dict:
        """Return a dictionary representation of the process."""
        if proc := self.get_process():
            return get_process_info(proc)
        return {}  # pragma: no cover
