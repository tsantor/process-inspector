import logging

from process_inspector.scriptcontrol.infrastructure.platform_runners import (
    run_bash_script,
)
from process_inspector.scriptcontrol.interface import ScriptInterface

logger = logging.getLogger(__name__)


class Script(ScriptInterface):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_bash_script(
            self.app_path,
            possible_paths=["/bin/bash", "/usr/bin/bash"],
        )
