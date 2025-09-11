import logging
import platform
import shlex
import subprocess
from functools import cached_property
from pathlib import Path

from .implementations import SupervisorCtl

logger = logging.getLogger(__name__)


class Service(SupervisorCtl):
    """macOS Supervisor Control"""

    use_sudo = False

    @cached_property
    def supervisor_path(self) -> Path:
        """Return the path to supervisorctl based on the architecture."""
        cmd = "sysctl -n sysctl.proc_translated"
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        # Rosetta Python on M1 or Non-Rosetta Python on M1
        if (platform.processor() == "i386" and "1" in proc.stdout.strip()) or (
            platform.processor() == "arm" and "0" in proc.stdout.strip()
        ):
            return Path("/opt/homebrew/bin/supervisorctl")
        # Intel
        return Path("/usr/local/bin/supervisorctl")
