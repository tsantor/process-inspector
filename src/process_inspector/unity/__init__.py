from process_inspector.utils.importutils import get_platform_module

platform_module = get_platform_module(__name__)

UnityApp = platform_module.UnityApp
