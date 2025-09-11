from process_inspector.utils.importutils import get_platform_module

platform_module = get_platform_module(__name__)

OperatingSystem = platform_module.OperatingSystem
