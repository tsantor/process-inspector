import logging
import subprocess

from .interface import OperatingSystemInterface

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemInterface):
    """OS X"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        logger.info("Reboot requested")
        cmd = ["sudo", "shutdown", "-r", "now"]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603
        return proc.returncode == 0
