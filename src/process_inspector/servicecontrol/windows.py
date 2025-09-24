import contextlib
import logging
import shlex
import subprocess

import psutil

from .interface import ServiceInterface

logger = logging.getLogger(__name__)


class Service(ServiceInterface):
    """Basic control of a Windows Service."""

    def __init__(self, name):
        super().__init__(name)
        self._service = self.get_service()
        self._pid = self._service.pid() if self._service else None
        # self._process = self.get_process()
        logger.info("Service: %s | Status: %s", name, self.status())

    def get_service(self):
        return psutil.win_service_get(self.name)

    def get_process(self) -> psutil.Process:
        return psutil.Process(self._pid)

    def is_running(self) -> bool:
        return self._service and self._service.status() == "running"

    def start(self) -> bool:
        """Start Service"""
        cmd = f'''powershell -command "Start-Service '{self.name}'"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop Service"""
        cmd = f'''powershell -command "Stop-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        cmd = f'''powershell -command "Restart-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603
        return proc.returncode == 0

    def status(self) -> str:
        """Return status string (e.g., 'Running', 'Stopped')."""
        return self._service.status().upper() if self._service else "ERROR"
