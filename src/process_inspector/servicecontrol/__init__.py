from process_inspector.utils.importutils import get_platform_module

from .implementations import SupervisorCtl  # noqa: F401
from .implementations import SystemCtl  # noqa: F401
from .linux import service_class_factory  # noqa: F401

platform_module = get_platform_module(__name__)

Service = platform_module.Service
