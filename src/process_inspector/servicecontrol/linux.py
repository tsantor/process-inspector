from functools import cached_property
from pathlib import Path

from .implementations import SupervisorCtl


class Service(SupervisorCtl):
    """Linux Supervisor Control"""

    @cached_property
    def supervisor_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [Path("/usr/bin/supervisorctl")]
        return next((path for path in possible_paths if path.is_file()), False)

    @cached_property
    def systemctl_path(self) -> Path:
        # Check if any of the possible paths contain the executable
        possible_paths = [Path("/usr/bin/systemctl")]
        return next((path for path in possible_paths if path.is_file()), False)
