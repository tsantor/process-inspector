from pathlib import Path

from .implementations import SupervisorCtl


class Service(SupervisorCtl):
    """Linux Supervisor Control"""

    use_sudo = True
    supervisor_path = Path("/usr/bin/supervisorctl")
