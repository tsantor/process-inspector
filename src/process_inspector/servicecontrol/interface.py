import logging
from abc import ABC
from abc import abstractmethod

import psutil

from process_inspector.utils.processutils import get_process_info

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """Basic control of a Service"""

    def __init__(self, name):
        self.name: str = name
        self._pid: int = None
        self._process: psutil.Process = None
        logger.info("Service name: %s", self.name)

    def pid(self) -> int | None:
        return self._pid

    def get_process(self) -> psutil.Process:
        return psutil.Process(self._pid)

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

    def as_dict(self) -> dict:
        return {
            "pid": self.pid(),
            "name": self.name,
            "is_running": self.is_running(),
            "status": self.status(),
        }

    def process_info(self) -> dict:
        if proc := (self._process or self._cached_process):
            return get_process_info(proc)
        return {}
