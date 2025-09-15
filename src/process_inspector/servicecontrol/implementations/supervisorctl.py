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

    supervisor_path = None

    @property
    def prefix(self):
        """Prefix with sudo if needed."""
        return "sudo" if self.use_sudo else ""

    def is_running(self) -> bool:
        """Determine if service is running."""
        cmd = f"{self.prefix} {self.supervisor_path} status {self.name}".strip()
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return "RUNNING" in proc.stdout.strip()

    def start(self) -> bool:
        """Start service"""
        cmd = f"{self.prefix} {self.supervisor_path} start {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        matches = ["started", "already started"]
        return any(x in proc.stdout.strip() for x in matches)

    def stop(self) -> bool:
        """Stop service"""
        cmd = f"{self.prefix} {self.supervisor_path} stop {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        matches = ["stopped", "not running"]
        return any(x in proc.stdout.strip() for x in matches)

    def restart(self) -> bool:
        """Restart service"""
        cmd = f"{self.prefix} {self.supervisor_path} restart {self.name}".strip()
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, text=True, capture_output=True
        )
        return "started" in proc.stdout.strip()
