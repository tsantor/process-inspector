from .implementations import SupervisorCtl
from .implementations import SystemCtl


class Service(SupervisorCtl):
    """Linux Supervisor Control"""

    # We default to SupervisorCtl for backward compatibility
    # If you want SystemCtl, use the factory function below


def service_class_factory(impl="supervisor"):
    """
    Factory to return the desired service control class for Linux.
    :param impl: "supervisor" or "systemctl"
    :return: Class (not instance)
    """
    if impl == "supervisor":
        return SupervisorCtl
    if impl == "systemctl":
        return SystemCtl
    msg = f"Invalid implementation: {impl}"
    raise ValueError(msg)
