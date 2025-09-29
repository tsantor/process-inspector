import logging
import re
import shlex
import subprocess
from pathlib import Path

import psutil

from process_inspector.utils.processutils import get_process_by_name

from .interface import AppInterface

logger = logging.getLogger(__name__)


PID_CREATE_TIME_TOLERANCE = 0.001


class App(AppInterface):
    """Basic control of a Mac App using Popen and psutil."""

    def __init__(self, app_path: Path):
        super().__init__(app_path)
        # Store process details similar to Windows
        self._process: psutil.Process | None = None
        self._pid: int | None = None
        self._create_time: float | None = None

    def reset_cache(self) -> None:
        """Clear cached process info."""
        self._process = None
        self._pid = None
        self._create_time = None

    def is_running(self) -> bool:
        """Check if the *specific* app instance is running."""
        if self._pid is None:
            # Fallback: check if the app is running (first run or manual restart)
            proc = get_process_by_name(self.app_path.stem)
            if not proc:
                return False

            # Found a running instance, adopt it
            self._process = proc
            self._pid = proc.pid
            try:
                self._create_time = proc.create_time()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.reset_cache()
                return False

        try:
            # Use cached process or look it up again
            p = self._process or psutil.Process(self._pid)
            if abs(p.create_time() - self._create_time) > PID_CREATE_TIME_TOLERANCE:
                self.reset_cache()
                return False

            # Check status
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            self.reset_cache()
            return False

    def open(self) -> bool:
        """
        Open app using the 'open' command and remember the PID we spawned.
        The `open` command is the standard way to launch .app bundles.
        """
        if self.is_running():
            return True

        # Use the 'open' command to launch the .app bundle
        try:
            cmd = ["open", str(self.app_path)]
            proc = subprocess.Popen(cmd)  # noqa: S603
            proc.wait(timeout=1.0)
        except FileNotFoundError:
            logger.exception("App path not found: %s", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app: %s", self.app_path)
            return False

        # Now, find the actual application process that 'open' started
        new_proc = get_process_by_name(self.app_path.stem)
        if not new_proc:
            logger.error(
                "Successfully called 'open' but couldn't find the new process."
            )
            return False

        self._pid = new_proc.pid
        try:
            self._process = new_proc
            self._create_time = self._process.create_time()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.reset_cache()
            return False

        return True

    def close(self) -> bool:
        """Close the running app we launched (terminate -> kill) and wait."""
        if not self.is_running():
            self.reset_cache()
            return True

        try:
            p = self._process or psutil.Process(self._pid)
        except psutil.NoSuchProcess:
            self.reset_cache()
            return True

        # Try graceful terminate (SIGTERM), then escalate (SIGKILL)
        try:
            p.terminate()
            p.wait(timeout=2.0)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                p.kill()
                p.wait(timeout=3.0)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning("Failed to kill process PID=%s", self._pid)

        self.reset_cache()
        return True

    def get_version(self) -> str:
        """
        Get version using mdls (Metadata List), which is reliable and
        doesn't use AppleScript. This part is already fine!
        """
        cmd = f'mdls -name kMDItemVersion "{self.app_path}"'
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
