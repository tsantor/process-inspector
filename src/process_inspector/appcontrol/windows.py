import logging
import re
import shlex
import subprocess

import psutil

from process_inspector.utils.processutils import get_process_by_name

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Windows App"""

    def is_running(self) -> bool:
        """Check if the application is running."""
        if self._process is None or self._pid is None:
            self._process = get_process_by_name(self.app_path)
            self._pid = self._process.pid if self._process else None

        if self._pid is not None:
            try:
                return psutil.Process(self._pid).is_running()
            except psutil.NoSuchProcess:
                self._process = None
                self._pid = None
                return False
        return False

    def open(self) -> bool:
        """Open app"""
        if self.is_running():
            return True

        cmd = f'START "" "{self.app_path}"'  # fails if spaces in filename
        cmd = cmd.replace("&", "^&")  # escape special characters
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, shell=True)  # noqa: S602
        return proc.returncode == 0

    def close(self) -> bool:
        """Close app"""
        if not self.is_running():
            return True

        cmd = f"Taskkill /PID {self._pid} /F"
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False)  # noqa: S603
        return proc.returncode == 0

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
