import logging
import re
import shlex
import subprocess

import psutil

from process_inspector.utils.processutils import get_process_by_name

from .interface import AppInterface

logger = logging.getLogger(__name__)


def debug_process_info(proc: psutil.Process) -> dict:
    return proc.as_dict(
        attrs=["pid", "name", "exe", "cmdline", "create_time", "status"]
    )


class App(AppInterface):
    """Basic control of a Windows App"""

    # def __init__(self, app_path: Path):
    #     super().__init__(app_path)

    def is_running(self) -> bool:
        """Check if the *specific* app instance is running."""
        if self._pid is None:
            # Fallback (first run, or after a manual kill outside our code)
            proc = get_process_by_name(self.app_path, newest=True)
            if not proc:
                self.reset_cache()
                return False

            # Found a running instance, adopt it
            self._process = proc
            self._pid = proc.pid
            logger.debug("Process: %s", debug_process_info(proc))
            try:
                self._create_time = proc.create_time()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                logger.warning("Process disappeared or access denied after lookup")
                self.reset_cache()
                return False

        try:
            p = self._process or psutil.Process(self._pid)
            # Guard against PID reuse: ensure it's the same process we started
            if self._create_time is not None:
                if abs(p.create_time() - self._create_time) > 1e-3:  # noqa: PLR2004
                    # Different process now occupies this PID
                    self.reset_cache()
                    return False

            # psutil quirk: is_running can be True for zombies; also check status
            return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            self.reset_cache()
            return False

    def open(self) -> bool:
        """Open app and remember the PID we spawned."""
        if self.is_running():
            return True

        # Launch the executable directly
        try:
            subprocess.Popen([str(self.app_path)])  # noqa: S603
        except FileNotFoundError:
            logger.exception("App not found: %s", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app: %s", self.app_path)
            return False

        # NOTE: On Windows, we won't always get the actual app process PID here,
        # especially for apps that use a launcher or helper process. We try to
        # find the actual app process by name below if needed.
        # time.sleep(1.0)  # Give it a moment to start
        # proc = get_process_by_name(self.app_path, newest=True)
        # if not proc:
        #     self.reset_cache()
        #     return False
        # self._process = proc
        # self._pid = proc.pid
        # logger.debug("Spawned %s with PID=%s", self.app_exe, self._pid)

        return True

    def close(self) -> bool:
        """Close the running app we launched (terminate → kill) and wait."""
        if not self.is_running():
            self.reset_cache()
            return True

        try:
            p = self._process or psutil.Process(self._pid)
        except psutil.NoSuchProcess:
            self.reset_cache()
            return True

        # Try graceful terminate, then escalate
        try:
            p.terminate()  # On Windows this is TerminateProcess under the hood
            p.wait(timeout=2.0)
            logger.debug("Terminated %s process PID=%s", self.app_exe, self._pid)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                p.kill()
                p.wait(timeout=3.0)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                # If it still won't die, consider it a failure but reset state
                logger.warning("Failed to kill process PID=%s", self._pid)

        self.reset_cache()
        return True

    def get_version(self) -> str:
        escaped_path = str(self.app_path).replace("\\", "\\\\")
        cmd = f"""powershell -Command '(Get-Item -Path "{escaped_path}").VersionInfo.ProductVersion'"""
        logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
