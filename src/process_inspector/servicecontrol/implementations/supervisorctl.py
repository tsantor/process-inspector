import logging
import shlex
import subprocess

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SupervisorCtl(ServiceInterface):
    """
    Supervisor Service

    NOTE: Supervisor returns exit codes that don't necessarily give us the
    status we want (exit codes other than 0 or 1) so we'll read the output
    instead.
    """

    def __init__(self, name):
        super().__init__(name)
        if not self.supervisor_path:
            msg = "supervisorctl executable not found"
            raise FileNotFoundError(msg)

        # Initialize with current PID if available
        current_pid = self.get_pid()
        if current_pid:
            self._cached_pid = current_pid
            self._cached_process = self._get_process_for_pid(current_pid)

        logger.info("Service: %s | Status: %s", name, self.status())

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        cmd = f"sudo {self.supervisor_path} pid {self.name}".strip()
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        if output.isdigit():
            return int(output)
        return None

    # def is_running(self) -> bool:
    #     """Determine if service is running."""
    #     cmd = f"sudo {self.supervisor_path} status {self.name}".strip()
    #     # logger.debug("Execute command: %s", cmd)
    #     proc = subprocess.run(
    #         shlex.split(cmd), check=False, text=True, capture_output=True
    #     )
    #     return "RUNNING" in proc.stdout.strip()

    # def is_running(self) -> bool:
    #     """Check if service is running."""
    #     # This will refresh PID/process if needed
    #     current_process = self.get_process()

    #     if not current_process:
    #         logger.debug("No process found for service '%s'", self.name)
    #         return False

    #     return self.status() == "RUNNING"

    def start(self) -> bool:
        """Start service"""
        cmd = f"sudo {self.supervisor_path} start {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        matches = ["started", "already started"]
        output = proc.stdout.strip().lower()
        return any(x in output for x in matches)

    def stop(self) -> bool:
        """Stop service"""
        cmd = f"sudo {self.supervisor_path} stop {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        matches = ["stopped", "not running"]
        output = proc.stdout.strip().lower()
        return any(x in output for x in matches)

    def restart(self) -> bool:
        """Restart service"""
        cmd = f"sudo {self.supervisor_path} restart {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        matches = ["started"]
        output = proc.stdout.strip().lower()
        return any(x in output for x in matches)

    def status(self) -> str:
        """Get service status (e.g., RUNNING, STOPPED, etc.)"""
        cmd = f"sudo {self.supervisor_path} status {self.name}".strip()
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        if output := proc.stdout.strip():
            parts = output.split()
            if len(parts) > 1:
                return parts[1].upper()
        return "--"
