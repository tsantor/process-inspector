import logging
import subprocess

from process_inspector.scriptcontrol.interface import ScriptInterface

logger = logging.getLogger(__name__)


def run_script(path: str) -> int | None:
    try:
        result = subprocess.run(  # noqa: S603
            [path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return None


class Script(ScriptInterface):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_script(self.app_path)
