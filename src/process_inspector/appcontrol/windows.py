import logging
import time

from process_inspector.appcontrol.infrastructure.platform_commands import (
    launch_windows_app,
)
from process_inspector.appcontrol.infrastructure.platform_commands import (
    read_windows_app_version,
)

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Windows App"""

    def open(self, timeout: float = 5.0) -> bool:
        """Open app and wait to grab its PID if possible."""
        if self.is_running():
            return True

        logger.info("Open app '%s'", self.app_exe)

        start_time = time.perf_counter()

        # Launch the executable directly
        try:
            launch_windows_app(self.app_path)
        except FileNotFoundError:
            logger.exception("App '%s' not found", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app '%s'", self.app_exe)
            return False

        # Wait for process to start so we can get its PID
        while not self.is_running():
            if time.perf_counter() - start_time > timeout:
                logger.warning(
                    "Timed out (%s secs) waiting for app '%s' to open",
                    timeout,
                    self.app_exe,
                )
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
        return read_windows_app_version(self.app_path)
