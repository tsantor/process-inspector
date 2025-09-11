from process_inspector.utils.importutils import get_platform_module

platform_module = get_platform_module(__name__)

get_teamviewer_info = platform_module.get_teamviewer_info
get_teamviewer_path = platform_module.get_teamviewer_path
is_teamviewer_installed = platform_module.is_teamviewer_installed

from .teamviewer import Teamviewer  # noqa: F401, E402
