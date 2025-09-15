import logging
import shlex
import subprocess

from process_inspector.utils.stringutils import extract_version

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Linux App. This is under the full assumption you are
    running apps under Supervisor."""

    def is_running(self) -> bool:
        """Determine if app is running."""
        logger.warning(
            "Linux App control is experimental and may not work as expected."
        )
        return False

    def open(self) -> bool:
        """Open app"""
        logger.warning(
            "Linux App control is experimental and may not work as expected."
        )
        return False

    def close(self) -> bool:
        """Close app"""
        logger.warning(
            "Linux App control is experimental and may not work as expected."
        )
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
