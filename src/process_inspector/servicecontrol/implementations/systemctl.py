import logging
import shlex
import subprocess

from process_inspector.servicecontrol.interface import ServiceInterface

logger = logging.getLogger(__name__)


class SystemCtl(ServiceInterface):
    """Linux System Ctl Service"""

    @property
    def prefix(self):
        """Prefix with sudo if needed."""
        return "sudo" if self.use_sudo else ""

    def is_running(self) -> bool:
        """Determine if service is running."""
        cmd = f"{self.prefix} systemctl status {self.name}".strip()
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return "active (running)" in proc.stdout.strip()

    def start(self) -> bool:
        """Start service"""
        cmd = f"{self.prefix} systemctl start {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop service"""
        cmd = f"{self.prefix} systemctl stop {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        cmd = f"{self.prefix} systemctl restart {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return proc.returncode == 0
