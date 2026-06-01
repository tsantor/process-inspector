import logging

from process_inspector.scriptcontrol.infrastructure.base import ScriptBase
from process_inspector.scriptcontrol.infrastructure.platform_runners import (
    run_windows_script,
)

logger = logging.getLogger(__name__)


class Script(ScriptBase):
    """Basic control of a Script which launches a child process."""

    def get_script_result(self) -> bool:
        """Get the boolean result of the script run."""
        return run_windows_script(self.app_path)
