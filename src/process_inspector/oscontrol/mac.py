import logging

from .infrastructure.base import OperatingSystemInterface

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemInterface):
    """OS X"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        cmd = ["sudo", "shutdown", "-r", "now"]
        return self._run_reboot_command(cmd)
