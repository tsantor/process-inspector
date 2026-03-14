from __future__ import annotations

from process_inspector.teamviewer.application.service import TeamviewerService
from process_inspector.teamviewer.infrastructure.repository import (
    build_teamviewer_controller,
)


def build_teamviewer_service(*, state_change_callback=None) -> TeamviewerService:
    controller = build_teamviewer_controller(
        state_change_callback=state_change_callback
    )
    return TeamviewerService(controller=controller)
