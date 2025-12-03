import logging
import subprocess
import time
from pathlib import Path

from process_inspector.appcontrol.interface import AppInterface

logger = logging.getLogger(__name__)


def run_script(path: Path) -> bool:
    try:
        result = subprocess.run(  # noqa: S603
            ["/opt/homebrew/bin/bash", path], check=True, capture_output=True, text=True
        )
        logger.info("Script executed successfully. Output: %s", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.info(
            "Script execution failed with return code %s. Error: %s",
            e.returncode,
            e.stderr,
        )
        return False


class Script(AppInterface):
    """Basic control of a Script which launches a child process."""

    def open(self) -> bool:
        """Run the script."""
        logger.info("Run script '%s'", self.app_name)

        start_time = time.perf_counter()
        # cmd = ["open", str(self.app_path)]

        # Manually update running state to immediately reflect change
        self._update_running_state(is_running=True)
        result = run_script(self.app_path)

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
