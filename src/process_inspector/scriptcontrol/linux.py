import logging
import subprocess
from pathlib import Path

from process_inspector.scriptcontrol.interface import ScriptInterface

logger = logging.getLogger(__name__)


def run_script(path: Path) -> bool:
    try:
        result = subprocess.run(  # noqa: S603
            ["/usr/bin/bash", path], check=True, capture_output=True, text=True
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


class Script(ScriptInterface):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_script(self.app_path)
