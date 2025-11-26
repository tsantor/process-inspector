import logging
import re
import subprocess
import time

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Mac App using Popen and psutil."""

    def open(self, timeout: float = 5.0) -> bool:  # noqa: PLR0911
        """Open app."""
        if self.is_running():
            return True

        logger.info("Open app '%s'", self.app_name)

        start_time = time.perf_counter()
        cmd = ["open", str(self.app_path)]

        # Use the 'open' command to launch the .app bundle
        try:
            proc = subprocess.Popen(  # noqa: S603
                cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
            _, stderr = proc.communicate(timeout=5)
            if stderr:
                logger.error("Error while opening app '%s': %s", self.app_name, stderr)
                return False
        except subprocess.TimeoutExpired:
            logger.error(  # noqa: TRY400
                "Timeout expired while opening app '%s'.",
                self.app_name,
            )
            proc.kill()  # Ensure the process is terminated
            return False
        except FileNotFoundError:
            logger.exception("App path not found '%s'", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app '%s'", self.app_name)
            return False

        # Wait for process to start so we can get its PID
        while not self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning(
                    "Timed out (%s secs) waiting for %s to open",
                    timeout,
                    self,
                )
                return False
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "App '%s' started successfully in %.3f seconds.",
            self.app_name,
            elapsed,
        )

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=True)
        return True

    def close(self, timeout: float = 3.0) -> bool:
        """Close app."""
        if not self.is_running():
            return True

        logger.info("Close app '%s'", self.app_name)

        start_time = time.perf_counter()
        cmd = f'tell application "{self.app_name}" to quit'

        try:
            subprocess.run(["osascript", "-e", cmd], check=True)  # noqa: S603, S607
            # logger.debug("App '%s' sent graceful quit request.", self.app_name)
        except subprocess.CalledProcessError as e:
            logger.error(  # noqa: TRY400
                "Failed to send quit signal to '%s' via AppleScript. %s",
                self.app_name,
                e,
            )
        except FileNotFoundError:
            logger.error(  # noqa: TRY400
                "'osascript' not found. Ensure you are on macOS."
            )

        # Wait a moment for the quit to complete
        while self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning(
                    "Timed out (%s secs) waiting for %s to close",
                    timeout,
                    self,
                )
                return super().close()
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "App '%s' quit successfully in %.3f seconds.",
            self.app_name,
            elapsed,
        )

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=False)
        return True

    def get_version(self) -> str:
        """
        Get version using mdls (Metadata List), which is reliable and
        doesn't use AppleScript.
        """
        # logger.info("Get app version '%s'", self.app_name)
        cmd = ["mdls", "-name", "kMDItemVersion", str(self.app_path)]
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            cmd, check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
