import logging
import subprocess
import time

from process_inspector.appcontrol.infrastructure.platform_commands import launch_mac_app
from process_inspector.appcontrol.infrastructure.platform_commands import quit_mac_app
from process_inspector.appcontrol.infrastructure.platform_commands import (
    read_mac_app_version,
)
from process_inspector.appcontrol.interface.router import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Mac App using Popen and psutil."""

    def open(self, timeout: float = 5.0) -> bool:  # noqa: PLR0911
        """Open app."""
        if self.is_running():
            return True

        logger.info("Open app '%s'", self.app_name)

        start_time = time.perf_counter()

        # Use the 'open' command to launch the .app bundle
        try:
            if not launch_mac_app(self.app_path):
                logger.error("Error while opening app '%s'", self.app_name)
                return False
        except subprocess.TimeoutExpired:
            logger.error(  # noqa: TRY400
                "Timeout expired while opening app '%s'.",
                self.app_name,
            )
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

        try:
            quit_mac_app(self.app_name)
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
        return read_mac_app_version(self.app_path)
