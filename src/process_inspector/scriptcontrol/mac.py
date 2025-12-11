import logging
import subprocess
from pathlib import Path

from process_inspector.scriptcontrol.interface import ScriptInterface

logger = logging.getLogger(__name__)


def get_bash_path() -> str:
    """Find the path to the bash executable on macOS."""
    # Order is important here (we prefer Homebrew installations)
    possible_paths = [
        "/opt/homebrew/bin/bash",  # Homebrew on Apple Silicon
        "/usr/local/bin/bash",  # Homebrew on Intel Macs
        "/bin/bash",
        "/usr/bin/bash",
    ]
    return next(
        (path for path in possible_paths if Path(path).exists()),
        None,
    ) or FileNotFoundError("Bash executable not found on this system.")


def run_script(path: Path) -> bool:
    try:
        subprocess.run(  # noqa: S603
            [get_bash_path(), path],
            check=True,
            capture_output=True,
            text=True,
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
