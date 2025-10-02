import logging
import shlex
import subprocess

# from functools import cached_property
import psutil

from .interface import ServiceInterface

logger = logging.getLogger(__name__)


class Service(ServiceInterface):
    """Basic control of a Windows Service."""

    def __init__(self, name):
        super().__init__(name)
        self._service = self.get_service()

        # Initialize with current PID if available
        current_pid = self.get_pid()
        if current_pid:
            self._cached_pid = current_pid
            self._cached_process = self._get_process_for_pid(current_pid)

        logger.info("Service: %s | Status: %s", name, self.status())

    def get_pid(self) -> int | None:
        return self._service.pid() if self._service else None

    def pid(self) -> int | None:
        """Get current PID, updating cache if it changed."""
        if not self._service:
            return None
        return super().pid()

    def get_service(self):
        """Get the service object."""
        try:
            return psutil.win_service_get(self.name)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to get service '%s': %s", self.name, e)  # noqa: TRY400
            return None

    def is_running(self) -> bool:
        """Check if service is running."""
        if not self._service:
            return False

        return super().is_running()

    def start(self) -> bool:
        """Start Service"""
        cmd = f'''powershell -command "Start-Service '{self.name}'"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603

        # Refresh service info after start attempt
        if proc.returncode == 0:
            # self._service = self.get_service()
            self.reset_cache()

        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop Service"""
        cmd = f'''powershell -command "Stop-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603

        # Clear cache after stop attempt since process will be gone
        if proc.returncode == 0:
            # self._service = self.get_service()
            self.reset_cache()

        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        cmd = f'''powershell -command "Restart-Service '{self.name}' -Force"'''
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(shlex.split(cmd), check=False, capture_output=True)  # noqa: S603

        # Refresh service info after restart attempt
        if proc.returncode == 0:
            # self._service = self.get_service()
            self.reset_cache()

        return proc.returncode == 0

    def status(self) -> str:
        """Return status string (e.g., 'RUNNING', 'STOPPED')."""
        if not self._service:
            return "--"

        try:
            return self._service.status().upper()
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to get status for service '%s': %s", self.name, e)  # noqa: TRY400
            return "--"
