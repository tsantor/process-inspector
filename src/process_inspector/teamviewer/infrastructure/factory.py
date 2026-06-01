from __future__ import annotations

import sys

from process_inspector.appcontrol import NativeApp
from process_inspector.servicecontrol.implementations import SystemCtl
from process_inspector.teamviewer import get_teamviewer_path


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
