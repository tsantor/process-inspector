import logging
import shlex
import subprocess

from process_inspector.utils.processutils import get_process_by_name
from process_inspector.utils.stringutils import extract_version

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Linux App. This is under the full assumption you are
    running apps under Supervisor."""

    def get_process(self):
        """Return the process object of the app."""
        return get_process_by_name(self.app_path)

    def is_running(self) -> bool:
        """Determine if app is running."""
        if self.service:
            return self.service.is_running()
        return False

    def open(self) -> bool:
        """Open app"""
        if self.service:
            return self.service.start()
        return False

    def close(self) -> bool:
        """Close app"""
        if self.service:
            return self.service.stop()
        return False

    def get_version(self) -> str:
        """Get the application's version."""
        cmd = f"{self.app_path} --version"
        logger.debug("Execute command: %s", cmd)
        try:
            proc = subprocess.run(  # noqa: S603
                shlex.split(cmd), check=True, text=True, capture_output=True
            )
            version = proc.stdout.strip()
            return extract_version(version)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("FileNotFoundError: Unable to get application version.")
        return "--"
