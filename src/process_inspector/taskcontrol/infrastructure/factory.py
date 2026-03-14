from __future__ import annotations

from process_inspector.taskcontrol.application.service import ScheduledTaskService
from process_inspector.taskcontrol.infrastructure.repository import PowerShellRunner


def build_task_service() -> ScheduledTaskService:
    return ScheduledTaskService(powershell_runner=PowerShellRunner())
