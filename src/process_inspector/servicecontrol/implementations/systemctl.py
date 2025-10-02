import logging
import shlex
import subprocess
from functools import cached_property
from pathlib import Path

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SystemCtl(ServiceInterface):
    """Linux System Ctl Service"""

    def __init__(self, name):
        super().__init__(name)
        if not self.service_control_path:
            msg = "service control executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

    @cached_property
    def service_control_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [Path("/usr/bin/systemctl")]
        return next((path for path in possible_paths if path.is_file()), False)

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
