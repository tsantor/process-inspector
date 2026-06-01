import logging

from .runtime.base import OperatingSystemBase

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemBase):
    """OS X"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        cmd = ["sudo", "shutdown", "-r", "now"]
        return self._run_reboot_command(cmd)
