from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod

from process_inspector.oscontrol.infrastructure.factory import build_reboot_service

logger = logging.getLogger(__name__)


class OperatingSystemBase(ABC):
    """Basic control of an OS."""

    def __init__(self):
        self._reboot_service = build_reboot_service()

    def _run_reboot_command(self, cmd: list[str]) -> bool:
        logger.info("Reboot requested")
        return self._reboot_service.reboot(cmd)

    @abstractmethod
    def reboot(self, name="Dashboard") -> bool:
        """Reboot computer."""
