import logging
from abc import ABC
from abc import abstractmethod

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """Basic control of a Service"""

    def __init__(self, name):
        self.name = name
        # TODO: Why do we keep instantiating this class?
        # TODO: Add a check to see if the service exists
        logger.debug("Service name: %s", self.name)

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

    def open(self) -> bool:
        """Alias so we can use a service like an app."""
        self.start()

    def close(self) -> bool:
        """Alias so we can use a service like an app."""
        self.stop()

    # @abstractmethod
    # def status(self) -> str:
    #     """Service status"""
    #     raise NotImplementedError(
    #         "This method should return a String: running, stopped or fatal"
    #     )

    def __repr__(self):
        return f"ServiceInterface('{self.name}')"

    def to_dict(self) -> dict:
        return {"name": self.name, "is_running": self.is_running()}
