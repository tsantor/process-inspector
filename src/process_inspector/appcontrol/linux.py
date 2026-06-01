import logging
import subprocess

from process_inspector.appcontrol.infrastructure.base import AppBase
from process_inspector.appcontrol.infrastructure.platform_commands import (
    read_linux_app_version,
)

logger = logging.getLogger(__name__)


class App(AppBase):
    """Basic control of a Linux App. This is under the full assumption you are
    running apps under Supervisor."""

    def is_running(self) -> bool:
        """Determine if app is running."""
        return False

    def open(self) -> bool:
        """Open app"""
        # Manually update running state to immediately reflect change
        # self._update_running_state(is_running=True)
        return False

    def close(self) -> bool:
        """Close app"""
        # Manually update running state to immediately reflect change
        # self._update_running_state(is_running=False)
        return False

    def get_version(self) -> str:
        """Get the application's version."""
        try:
            return read_linux_app_version(self.app_path)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("FileNotFoundError: Unable to get application version.")
        return "--"
