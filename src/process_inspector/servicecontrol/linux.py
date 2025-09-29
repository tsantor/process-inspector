from functools import cached_property
from pathlib import Path

from .implementations import SupervisorCtl

# from .implementations import SystemCtl


class Service(SupervisorCtl):
    """Linux Supervisor Control"""

    # def get_controller(name, impl="supervisor"):
    #     if impl == "supervisor":
    #         return SupervisorCtl(name)
    #     if impl == "systemctl":
    #         return SystemCtl(name)

    #     msg = f"Unknown implementation: {impl}"
    #     raise ValueError(msg)

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

    @cached_property
    def service_control_path(self) -> Path:
        """Get path to the service executable if available."""
        return self.supervisor_path
