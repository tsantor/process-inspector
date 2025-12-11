import logging
import subprocess
from pathlib import Path

from process_inspector.scriptcontrol.interface import ScriptInterface

logger = logging.getLogger(__name__)


def run_script(
    path: Path,
) -> bool:
    try:
        # Use the file path directly as the command
        cmd = [str(path)]

        subprocess.run(  # noqa: S602
            cmd,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
        )
        logger.info("Script '%s' executed successfully.", path)
        return True
    except subprocess.CalledProcessError as e:
        logger.info(
            "Script '%s' execution failed with return code %s. Error: %s",
            path,
            e.returncode,
            e.stderr.strip(),
        )
        return False
    except FileNotFoundError:
        logger.warning("Script '%s' not found", path)
        return False


class Script(ScriptInterface):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_script(self.app_path)
