import logging
import re
import shlex
import subprocess

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Mac App."""

    def is_running(self) -> bool:
        """Determine if app is running."""
        cmd = f"""osascript -e 'application "{self.app_path.stem}" is running'"""
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=True, capture_output=True, text=True
        )
        return proc.stdout.strip() == "true"

    def open(self) -> bool:
        """Open app"""
        cmd = f"""osascript -e 'tell application "{self.app_path.stem}" to activate'"""
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True)  # noqa: S603
        return proc.returncode == 0

    def close(self) -> bool:
        """Close app"""
        if not self.is_running():
            return True

        cmd = f"""osascript -e 'tell application "{self.app_path.stem}" to quit'"""
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True)  # noqa: S603
        return proc.returncode == 0

    def get_version(self) -> str:
        """Get version"""
        cmd = f'mdls -name kMDItemVersion "{self.app_path}"'
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
