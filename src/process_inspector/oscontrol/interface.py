import logging
from abc import ABC
from abc import abstractmethod

logger = logging.getLogger(__name__)


class OperatingSystemInterface(ABC):
    """Basic control of an OS"""

    @abstractmethod
    def reboot(self, name="Dashboard") -> bool:
        """Reboot computer."""
