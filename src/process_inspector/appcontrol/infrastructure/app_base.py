from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path

from process_inspector.appcontrol.infrastructure.factory import build_runtime_service

logger = logging.getLogger(__name__)


class AppControllerBase(ABC):
    """Basic control of an App."""

    def __init__(self, app_path: Path, state_change_callback=None):
        self.app_path = Path(app_path)
        self.app_exe = self.app_path.name
        self.app_name = self.app_path.stem
        self._runtime = build_runtime_service(
            state_change_callback=state_change_callback
        )

        if not self.is_installed():
            logger.warning(
                "App path does not exist: '%s'", app_path
            )  # pragma: no cover

        self.is_running()

    def __str__(self) -> str:
        return f"'{self.app_name} (PID: {self.pid})"

    def reset_cache(self) -> None:
        self._runtime.reset_cache()

    @property
    def pid(self) -> int | None:
        return self._runtime.pid

    def is_installed(self) -> bool:
        return self.app_path.exists()

    def is_running(self) -> bool:
        return self._runtime.is_running(self.app_path, self)

    def _update_running_state(self, is_running: bool) -> None:
        self._runtime.update_running_state(self, is_running=is_running)

    @abstractmethod
    def open(self) -> bool:
        """Open app."""

    def close(self, timeout: float = 5.0) -> bool:
        return self._runtime.close(self.app_path, self, timeout=timeout)

    @abstractmethod
    def get_version(self) -> str: ...

    @cached_property
    def version(self) -> str:
        return self.get_version()

    @cached_property
    def install_date(self) -> datetime | None:
        if self.is_installed() is False:
            return None
        tz = datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(self.app_path.stat().st_mtime, tz=tz)

    @cached_property
    def install_date_short(self) -> str | None:
        if self.install_date is None:
            return None
        return self.install_date.strftime("%Y-%m-%d")

    @cached_property
    def install_date_human_short(self) -> str | None:
        return self._runtime.install_date_human_short(self.install_date)

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
        return self._cached_dict

    def get_last_seen_str(self) -> str | None:
        return self._runtime.get_last_seen_str()

    def process_info(self) -> dict:
        return self._runtime.process_info(self)
