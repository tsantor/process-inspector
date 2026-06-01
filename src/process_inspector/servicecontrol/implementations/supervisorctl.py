import logging
import re
import subprocess
import sys
import time
from functools import cached_property
from pathlib import Path

from process_inspector.servicecontrol.runtime.controller_base import (
    ServiceControllerBase,
)

logger = logging.getLogger(__name__)


class SupervisorCtl(ServiceControllerBase):
    """
    Supervisor Service

    NOTE: Supervisor returns exit codes that don't necessarily give us the
    status we want (exit codes other than 0 or 1) so we'll read the output
    instead.
    """

    _command_cache_ttl_seconds = 5.0

    def __init__(self, name, state_change_callback=None):
        super().__init__(name, state_change_callback)
        self._command_cache: dict[str, tuple[float, object]] = {}
        if not self.service_control_path:
            msg = "'supervisorctl' executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

    def _reset_command_cache(self) -> None:
        self._command_cache.clear()

    def _get_cached_output(self, cache_key: str) -> str | None:
        cached = self._command_cache.get(cache_key)
        if not cached:
            return None
        now = time.monotonic()
        if now - cached[0] <= self._command_cache_ttl_seconds:
            return str(cached[1])
        return None

    def _run_supervisorctl(self, *args: str, cache_key: str | None = None) -> str:
        if cache_key:
            cached_output = self._get_cached_output(cache_key)
            if cached_output is not None:
                return cached_output

        if ".local/bin" in str(self.service_control_path):
            cmd = [str(self.service_control_path), *args]
        else:
            cmd = ["sudo", str(self.service_control_path), *args]
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        if cache_key:
            # Timestamp when the command completes so TTL measures staleness of data.
            self._command_cache[cache_key] = (time.monotonic(), output)
        return output

    @cached_property
    def service_control_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        if sys.platform == "darwin":
            possible_paths = [
                Path("/opt/homebrew/bin/supervisorctl"),
                Path("/usr/local/bin/supervisorctl"),
                Path("~/.local/bin/supervisorctl").expanduser(),
            ]
        else:
            possible_paths = [Path("/usr/bin/supervisorctl")]
        return next((path for path in possible_paths if path.is_file()), False)

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        status_output = self._get_cached_output("status")
        if status_output:
            pid_match = re.search(
                r"\bpid\s+(\d+)\b", status_output, flags=re.IGNORECASE
            )
            if pid_match and int(pid_match.group(1)) > 0:
                return int(pid_match.group(1))

        output = self._run_supervisorctl("pid", self.name, cache_key="pid")
        if output.isdigit() and int(output) > 0:
            return int(output)
        return None

    def _refresh_running_state(self) -> bool:
        """Refresh cached state from current supervisor status output."""
        running = self.status() in ["RUNNING", "SLEEPING"]
        self._update_running_state(is_running=running)
        return running

    def start(self, timeout: float = 5.0) -> bool:
        """Start service"""
        logger.info("Start service '%s'", self.name)

        start_time = time.perf_counter()
        output = self._run_supervisorctl("start", self.name)
        matches = ["started", "already started"]
        result = any(x in output.lower() for x in matches)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' started successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._refresh_running_state()
        return result

    def stop(self, timeout: float = 5.0) -> bool:
        """Stop service"""
        logger.info("Stop service '%s'", self.name)

        start_time = time.perf_counter()
        output = self._run_supervisorctl("stop", self.name)
        matches = ["stopped", "not running"]
        result = any(x in output.lower() for x in matches)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' quit successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._refresh_running_state()
        return result

    def restart(self) -> bool:
        """Restart service"""
        logger.info("Restart service '%s'", self.name)

        start_time = time.perf_counter()
        output = self._run_supervisorctl("restart", self.name)
        matches = ["started"]
        result = any(x in output.lower() for x in matches)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Service '%s' restarted successfully in %.3f seconds.",
            self.name,
            elapsed,
        )

        self.reset_cache()
        self._refresh_running_state()
        return result

    def status(self) -> str:
        """Get service status (e.g., RUNNING, STOPPED, etc.)"""
        output = self._run_supervisorctl("status", self.name, cache_key="status")
        parts = output.split()
        if len(parts) > 1:
            return parts[1].upper()
        return "--"  # pragma: no cover
