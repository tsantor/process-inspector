import logging
from functools import cached_property
from pathlib import Path

from .implementations import SupervisorCtl

logger = logging.getLogger(__name__)


class Service(SupervisorCtl):
    """macOS Supervisor Control"""

    @cached_property
    def supervisor_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [
            Path("/opt/homebrew/bin/supervisorctl"),
            Path("/usr/local/bin/supervisorctl"),
        ]
        return next((path for path in possible_paths if path.is_file()), False)

    @cached_property
    def service_control_path(self) -> Path:
        """Get path to the service executable if available."""
        return self.supervisor_path
