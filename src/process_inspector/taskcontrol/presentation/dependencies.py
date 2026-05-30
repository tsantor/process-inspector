from __future__ import annotations

from process_inspector.taskcontrol.infrastructure.factory import build_task_service


def get_task_service():
    return build_task_service()
