import logging

from .infrastructure.base import OperatingSystemBase

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemBase):
    """Windows"""

    def reboot(self, name="Dashboard") -> bool:  # pragma: no cover
        """Reboot computer"""
        cmd = [
            "shutdown",
            "/r",
            "/f",
            "/c",
            f"Remote Reboot from {name}",
        ]
        return self._run_reboot_command(cmd)
