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
        # self._cached_pid = None
        # self._cached_process = None

        # Initialize with current PID if available
        current_pid = self._service.pid() if self._service else None
        if current_pid:
            self._cached_pid = current_pid
            self._cached_process = self._get_process_for_pid(current_pid)

        # logger.info("Service: %s | Status: %s", name, self.status())

    def pid(self) -> int | None:
        """Get current PID, updating cache if it changed."""
        if not self._service:
            return None

        current_pid = self._service.pid()

        # Update cache if PID changed
        if current_pid != self._cached_pid:
            self._cached_pid = current_pid
            if current_pid:
                self._cached_process = self._get_process_for_pid(current_pid)
            else:
                self._cached_process = None

        return self._cached_pid

    # def get_process(self) -> psutil.Process | None:
    #     """Get process object, fetching only if PID changed."""
    #     # Ensure PID is up to date (this will update cache if needed)
    #     current_pid = self.pid()

    #     if not current_pid:
    #         return None

    #     return self._cached_process

    def _get_process_for_pid(self, pid: int) -> psutil.Process | None:
        """Helper to safely create Process object."""
        try:
            return psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning("Failed to get process for PID %d: %s", pid, e)
            return None

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

        # This will refresh PID/process if needed
        current_process = self.get_process()

        if not current_process:
            logger.debug("No process found for service '%s'", self.name)
            return False

        return self.status() == "RUNNING"

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
            return "ERROR"

        try:
            return self._service.status().upper()
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to get status for service '%s': %s", self.name, e)  # noqa: TRY400
            return "ERROR"
