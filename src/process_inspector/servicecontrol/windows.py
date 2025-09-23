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
        self.service = self.get_service()

        if self.service:
            logger.debug("%s service found | PID: %s", self.name, self.service.pid())
        else:
            logger.warning("%s service not found", self.name)

    def get_service(self):
        """Get Windows Service by name."""
        with contextlib.suppress(psutil.NoSuchProcess):
            return psutil.win_service_get(self.name)

    def is_running(self) -> bool:
        return self.service and self.service.status() == "running"

    def start(self) -> bool:
        """Start Service"""
        cmd = f'''powershell -command "Start-Service '{self.name}'"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True)  # noqa: S603
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop Service"""
        cmd = f'''powershell -command "Stop-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True)  # noqa: S603
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        cmd = f'''powershell -command "Restart-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=True)  # noqa: S603
        return proc.returncode == 0

    def status(self) -> str:
        """Return status string (e.g., 'Running', 'Stopped')."""
        cmd = f'''powershell -command "Get-Service -Name '{self.name}'"'''
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=True, capture_output=True, text=True
        )
        output = proc.stdout.strip().splitlines()
        # Find the line after the header (skip the first two lines)
        if len(output) >= 3:  # noqa: PLR2004
            status_line = output[2]
            return status_line.split()[0].upper()
        return "--"
