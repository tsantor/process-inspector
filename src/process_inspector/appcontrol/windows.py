import logging
import re
import shlex
import subprocess

from process_inspector.utils.processutils import get_process_by_name
from process_inspector.utils.processutils import is_process_running_by_name

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Windows App"""

    def get_process(self):
        """Return the process object of the app."""
        return get_process_by_name(self.app_path)

    def is_running(self) -> bool:
        """Determine if app is running."""
        return is_process_running_by_name(self.app_path)

    def open(self) -> bool:
        """Open app"""
        if not is_process_running_by_name(self.app_path):
            cmd = f'START "" "{self.app_path}"'  # fails if spaces in filename
            cmd = cmd.replace("&", "^&")  # escape special characters
            logger.debug("Execute command: %s", cmd)
            subprocess.run(shlex.split(cmd), check=True, shell=True)  # noqa: S602
        return True

    def close(self) -> bool:
        """Close app"""
        if process := get_process_by_name(self.app_path):
            cmd = f'Taskkill /IM "{process.name()}" /F'
            logger.debug("Execute command: %s", cmd)
            proc = subprocess.run(shlex.split(cmd), check=True, capture_output=True)  # noqa: S603
            return proc.returncode == 0
        return True

    def get_version(self) -> str:
        escaped_path = str(self.app_path).replace("\\", "\\\\")
        cmd = f"""powershell -Command '(Get-Item -Path "{escaped_path}").VersionInfo.ProductVersion'"""
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
