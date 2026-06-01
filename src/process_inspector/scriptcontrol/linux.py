import logging

from process_inspector.scriptcontrol.runtime.base import ScriptBase
from process_inspector.scriptcontrol.runtime.platform_runners import run_bash_script

logger = logging.getLogger(__name__)


class Script(ScriptBase):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_bash_script(
            self.app_path,
            possible_paths=["/bin/bash", "/usr/bin/bash"],
        )
