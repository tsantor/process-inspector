import logging
import re
import subprocess
import time

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Windows App"""

    def open(self, timeout: float = 3.0) -> bool:
        """Open app and wait to grab its PID if possible."""
        if self.is_running():
            return True

        logger.info("Open app '%s'", self.app_exe)

        start_time = time.perf_counter()

        # Launch the executable directly
        try:
            subprocess.Popen([str(self.app_path)])  # noqa: S603
        except FileNotFoundError:
            logger.exception("App '%s' not found", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app '%s'", self.app_exe)
            return False

        # Wait for process to start so we can get its PID
        while not self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning("Timed out waiting for app '%s' to start", self.app_exe)
                return False
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "App '%s' started successfully in %.3f seconds.",
            self.app_exe,
            elapsed,
        )

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=True)
        return True

    def get_version(self) -> str:
        escaped_path = str(self.app_path).replace("\\", "\\\\")
        cmd = [
            "powershell",
            "-command",
            f"""(Get-Item -Path "{escaped_path}").VersionInfo.ProductVersion""",
        ]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
