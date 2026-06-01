import logging
import subprocess
import time
from functools import cached_property
from pathlib import Path

from process_inspector.servicecontrol.infrastructure.controller_base import (
    ServiceControllerBase,
)

logger = logging.getLogger(__name__)


class SystemCtl(ServiceControllerBase):
    """Linux System Ctl Service"""

    _command_cache_ttl_seconds = 3.0

    def __init__(self, name, state_change_callback=None):
        super().__init__(name, state_change_callback)
        self._command_cache: dict[str, tuple[float, object]] = {}
        if not self.service_control_path:
            msg = "'systemctl' executable not found"  # pragma: no cover
            raise FileNotFoundError(msg)  # pragma: no cover

    def _reset_command_cache(self) -> None:
        self._command_cache.clear()

    def _run_systemctl(self, *args: str, cache_key: str | None = None) -> str:
        if cache_key:
            cached = self._command_cache.get(cache_key)
            if (
                cached
                and time.monotonic() - cached[0] <= self._command_cache_ttl_seconds
            ):
                return str(cached[1])

        cmd = ["sudo", str(self.service_control_path), *args]
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )
        output = proc.stdout.strip()
        if cache_key:
            # Timestamp when the command completes so TTL measures staleness of data.
            self._command_cache[cache_key] = (time.monotonic(), output)
        return output

    def _run_systemctl_proc(self, *args: str) -> subprocess.CompletedProcess:
        cmd = ["sudo", str(self.service_control_path), *args]
        return subprocess.run(  # noqa: S603
            cmd, check=False, text=True, capture_output=True
        )

    @cached_property
    def service_control_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [Path("/usr/bin/systemctl")]
        return next((path for path in possible_paths if path.is_file()), False)

    def get_pid(self) -> int | None:
        """Get PID of the service if running, else None."""
        show_data = self._read_show_properties()
        main_pid = show_data.get("MainPID", "")
        if main_pid.isdigit():
            return int(main_pid)
        return None

    def is_running(self) -> bool:
        """Check if service is running."""
        # This seems to be faster than checking the process
        status = self.status()
        return status == "RUNNING"

    def start(self) -> bool:
        """Start service"""
        logger.info("Start service '%s'", self.name)
        proc = self._run_systemctl_proc("start", self.name)
        self.reset_cache()
        return proc.returncode == 0

    def stop(self) -> bool:
        """Stop service"""
        logger.info("Stop service '%s'", self.name)
        proc = self._run_systemctl_proc("stop", self.name)
        self.reset_cache()
        return proc.returncode == 0

    def restart(self) -> bool:
        """Restart service"""
        logger.info("Restart service '%s'", self.name)
        proc = self._run_systemctl_proc("restart", self.name)
        self.reset_cache()
        return proc.returncode == 0

    def status(self) -> str:
        """Get service status"""
        show_data = self._read_show_properties()
        load_state = show_data.get("LoadState", "").lower()
        if load_state in ["not-found", "masked"]:
            return "--"

        active_state = show_data.get("ActiveState", "").lower()
        sub_state = show_data.get("SubState", "").lower()
        state = f"{active_state}:{sub_state}"

        status_map = {
            "active:running": "RUNNING",
            "inactive:dead": "STOPPED",
            "failed:failed": "FAILED",
            "activating:start": "STARTING",
            "deactivating:stop": "STOPPING",
        }
        if mapped := status_map.get(state):
            return mapped
        if active_state == "active":
            return "RUNNING"
        if active_state == "inactive":
            return "STOPPED"
        if active_state == "failed":
            return "FAILED"
        return "--"

    def _read_show_properties(self) -> dict[str, str]:
        output = self._run_systemctl("show", self.name, cache_key="show")
        props: dict[str, str] = {}
        for line in output.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            props[key] = value.strip()
        return props
