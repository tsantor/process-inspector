import logging
import subprocess
import sys
import time
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
        if output.isdigit() and int(output) > 0:
            return int(output)
        return None

    # TODO: Causing issues with is_running caching?
    # def is_running(self) -> bool:
    #     """Check if service is running."""
    #     # NOTE: We override the base class method here to use supervisorctl
    #     # This seems to be faster than checking the process
    #     status = self.status()
    #     running = status in ["RUNNING", "SLEEPING"]
    #     self._last_seen = datetime.now(tz=UTC)
    #     self._update_running_state(is_running=running)
    #     return running

    def start(self, timeout: float = 3.0) -> bool:
        """Start service"""
        logger.info("Start service '%s'", self.name)

        start_time = time.perf_counter()
        cmd = ["sudo", str(self.service_control_path), "start", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["started", "already started"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        # Wait for process to start so we can get its PID
        while not self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning("Timed out waiting for app '%s' to start", self.app_name)
                return False
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' started successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._update_running_state(is_running=result)
        return result

    def stop(self, timeout: float = 3.0) -> bool:
        """Stop service"""
        logger.info("Stop service '%s'", self.name)

        start_time = time.perf_counter()
        cmd = ["sudo", str(self.service_control_path), "stop", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["stopped", "not running"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        # Wait a moment for the quit to complete
        while self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning("Timed out waiting for %s to stop", self)
                return super().close()
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' quit successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._update_running_state(is_running=result)
        return result

    def restart(self) -> bool:
        """Restart service"""
        logger.info("Restart service '%s'", self.name)

        start_time = time.perf_counter()
        cmd = ["sudo", str(self.service_control_path), "restart", self.name]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        matches = ["started"]
        output = proc.stdout.strip().lower()
        result = any(x in output for x in matches)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' restarted successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._update_running_state(is_running=False)
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
