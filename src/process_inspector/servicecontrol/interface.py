import logging
from abc import ABC
from abc import abstractmethod

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """Basic control of a Service"""

    def __init__(self, name):
        self.name = name
        logger.debug("Service name: %s", self.name)
        # TODO: Add a check to see if the service exists

    @abstractmethod
    def is_running(self) -> bool:
        """Determine if service is running"""

    @abstractmethod
    def start(self) -> bool:
        """Start service"""

    @abstractmethod
    def stop(self) -> bool:
        """Stop service"""

    @abstractmethod
    def restart(self) -> bool:
        """Restart service"""

    @abstractmethod
    def status(self) -> str:
        """Service status"""

    def open(self) -> bool:
        """Alias so we can use a service like an app."""
        return self.start()

    def close(self) -> bool:
        """Alias so we can use a service like an app."""
        return self.stop()

    def __repr__(self):
        return f"Service('{self.name}')"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "is_running": self.is_running(),
            "status": self.status(),
        }
