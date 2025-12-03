import logging
import time
from abc import abstractmethod

from process_inspector.appcontrol.interface import AppInterface

logger = logging.getLogger(__name__)


class ScriptInterface(AppInterface):
    """Basic control of a Script which launches a child process."""

    def open(self) -> bool:
        """Run the script."""
        logger.info("Run script '%s'", self.app_name)

        start_time = time.perf_counter()

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=True)
        result = self.get_script_result()

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "Script '%s' ran in %.3f seconds.",
            self.app_name,
            elapsed,
        )

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=False)
        return result

    def run(self) -> bool:
        """Run the script (alias for open)."""
        return self.open()

    def get_version(self) -> str:
        return "--"

    @abstractmethod
    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        # return run_script(self.app_path)
