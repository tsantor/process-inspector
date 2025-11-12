import logging
import subprocess
from functools import cached_property
from pathlib import Path

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SystemCtl(ServiceInterface):
    """Linux System Ctl Service"""

    def __init__(self, name, state_change_callback=None):
        super().__init__(name, state_change_callback)
        if not self.service_control_path:
            msg = "'systemctl' executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

    @cached_property
    def service_control_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [Path("/usr/bin/systemctl")]
        return next((path for path in possible_paths if path.is_file()), False)

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        # cmd = f"sudo {self.service_control_path} show --property MainPID --value {self.name}".strip()
        cmd = [
            "sudo",
            str(self.service_control_path),
            "show",
            "--property",
            "MainPID",
            "--value",
            self.name,
        ]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        if output.isdigit():
            return int(output)
        return None

    def is_running(self) -> bool:
        """Check if service is running."""
        # This seems to be faster than checking the process
        status = self.status()
        return status == "RUNNING"

    def start(self) -> bool:
        """Start service"""
        logger.info("Start service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "start", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop service"""
        logger.info("Stop service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "stop", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        logger.info("Restart service '%s'", self.name)
        cmd = ["sudo", str(self.service_control_path), "restart", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def status(self) -> str:
        """Get service status"""
        cmd = ["sudo", str(self.service_control_path), "status", self.name]
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
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
