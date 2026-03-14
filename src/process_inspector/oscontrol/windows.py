import logging

from .interface import OperatingSystemInterface

logger = logging.getLogger(__name__)


class OperatingSystem(OperatingSystemInterface):
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
