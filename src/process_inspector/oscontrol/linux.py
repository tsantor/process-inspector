import logging

from .infrastructure.base import OperatingSystemBase

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemBase):
    """Linux"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        cmd = ["sudo", "reboot"]
        return self._run_reboot_command(cmd)
