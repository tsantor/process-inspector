import logging
import shlex
import subprocess

from .interface import OperatingSystemInterface

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemInterface):
    """Windows"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        cmd = f'shutdown /r /f /c "Remote Reboot from {name}"'
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True, capture_output=True)  # noqa: S603
        return proc.returncode == 0
