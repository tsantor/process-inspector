from __future__ import annotations

from process_inspector.taskcontrol.infrastructure.repository import PowerShellRunner
from process_inspector.taskcontrol.infrastructure.task_service import (
    ScheduledTaskService,
)


def build_task_service() -> ScheduledTaskService:
    return ScheduledTaskService(powershell_runner=PowerShellRunner())
