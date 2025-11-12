import logging
import subprocess
import sys
from functools import cached_property
from pathlib import Path

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SupervisorCtl(ServiceInterface):
    """
    Supervisor Service

    NOTE: Supervisor returns exit codes that don't necessarily give us the
    status we want (exit codes other than 0 or 1) so we'll read the output
    instead.
    """

    def __init__(self, name, state_change_callback=None):
        super().__init__(name, state_change_callback)
        if not self.service_control_path:
            msg = "'supervisorctl' executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

        # Initialize with current PID if available
        current_pid = self.get_pid()
        if current_pid:
            self._cached_pid = current_pid
            self._cached_process = self._get_process_for_pid(current_pid)

        # logger.info("Service: %s | Status: %s", name, self.status())

    @cached_property
    def service_control_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        if sys.platform == "darwin":
            possible_paths = [
                Path("/opt/homebrew/bin/supervisorctl"),
                Path("/usr/local/bin/supervisorctl"),
            ]
        else:
            possible_paths = [Path("/usr/bin/supervisorctl")]
        return next((path for path in possible_paths if path.is_file()), False)

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        cmd = ["sudo", str(self.service_control_path), "pid", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        if output.isdigit():
            return int(output)
        return None

    def is_running(self):
        # This seems to be faster than checking the process
        status = self.status()
        return status in ["RUNNING", "SLEEPING"]

    def start(self) -> bool:
        """Start service"""
        logger.info("Start service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "start", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["started", "already started"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        self.reset_cache()
        return result

    def stop(self) -> bool:
        """Stop service"""
        logger.info("Stop service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "stop", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["stopped", "not running"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        self.reset_cache()
        return result

    def restart(self) -> bool:
        """Restart service"""
        logger.info("Restart service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "restart", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["started"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        self.reset_cache()
        return result

    def status(self) -> str:
        """Get service status (e.g., RUNNING, STOPPED, etc.)"""
        cmd = ["sudo", str(self.service_control_path), "status", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        parts = output.split()
        if len(parts) > 1:
            return parts[1].upper()
        return "--"  # pragma: no cover
