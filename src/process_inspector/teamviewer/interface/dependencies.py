from __future__ import annotations

from process_inspector.teamviewer.infrastructure.factory import build_teamviewer_service


def get_teamviewer_service(*, state_change_callback=None):
    return build_teamviewer_service(state_change_callback=state_change_callback)
