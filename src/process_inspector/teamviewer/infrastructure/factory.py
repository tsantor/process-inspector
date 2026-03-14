from __future__ import annotations

import sys

from process_inspector.servicecontrol.implementations import SystemCtl
from process_inspector.teamviewer.application.service import TeamviewerService

if sys.platform == "darwin":
    from process_inspector.appcontrol.mac import App as NativeApp
    from process_inspector.teamviewer.mac import get_teamviewer_path
elif sys.platform == "win32":
    from process_inspector.appcontrol.windows import App as NativeApp
    from process_inspector.teamviewer.windows import get_teamviewer_path
else:
    from process_inspector.appcontrol.linux import App as NativeApp
    from process_inspector.teamviewer.linux import get_teamviewer_path


def build_teamviewer_controller(*, state_change_callback=None):
    if sys.platform == "linux":
        return SystemCtl(
            "teamviewerd.service",
            state_change_callback=state_change_callback,
        )
    return NativeApp(
        get_teamviewer_path(),
        state_change_callback=state_change_callback,
    )


def build_teamviewer_service(*, state_change_callback=None) -> TeamviewerService:
    controller = build_teamviewer_controller(
        state_change_callback=state_change_callback
    )
    return TeamviewerService(controller=controller)
