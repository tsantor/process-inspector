import logging
import shlex
import subprocess

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SystemCtl(ServiceInterface):
    """Linux System Ctl Service"""

    def __init__(self, name):
        super().__init__(name)
        if not self.service_control_path:
            msg = "service control executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        cmd = f"sudo {self.service_control_path} show --property MainPID --value {self.name}".strip()
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
    #     cmd = f"sudo {self.service_control_path} status {self.name}".strip()
    #     # logger.debug("Execute command: %s", cmd)
    #     proc = subprocess.run(
    #         shlex.split(cmd), check=False, text=True, capture_output=True
    #     )
    #     return "active (running)" in proc.stdout.strip().lower()

    def is_running(self) -> bool:
        """Check if service is running."""
        # This will refresh PID/process if needed
        current_process = self.get_process()

        if not current_process:
            logger.debug("No process found for service '%s'", self.name)
            return False

        return self.status() == "RUNNING"

    def start(self) -> bool:
        """Start service"""
        cmd = f"sudo {self.service_control_path} start {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop service"""
        cmd = f"sudo {self.service_control_path} stop {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        cmd = f"sudo {self.service_control_path} restart {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def status(self) -> str:
        """Get service status"""
        cmd = f"sudo {self.service_control_path} status {self.name}".strip()
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip().lower()

        if "could not be found" in output:
            return "--"

        status_map = {
            "active (running)": "RUNNING",
            "inactive (dead)": "STOPPED",
            "failed": "FAILED",
            "activating (start)": "STARTING",
            "deactivating (stop)": "STOPPING",
        }
        for key, value in status_map.items():
            if key in output:
                return value
        return "--"
