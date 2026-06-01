from __future__ import annotations

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

TASK_STATE_MAP = {
    0: "UNKNOWN",
    1: "DISABLED",
    2: "QUEUED",
    3: "READY",
    4: "RUNNING",
}


class ScheduledTaskService:
    def __init__(self, powershell_runner):
        self._runner = powershell_runner

    def fetch_task_data(self, task_name: str) -> dict | None:
        command = [
            f"Get-ScheduledTask -TaskName '{task_name}' -ErrorAction Stop |",
            "Select-Object -Property TaskName, State, @{Name='LastTaskResult'; Expression={(Get-ScheduledTaskInfo $_).LastTaskResult}}, @{Name='LastRunTime'; Expression={(Get-ScheduledTaskInfo $_).LastRunTime.ToString('o')}} |",
            "ConvertTo-Json -Compress",
        ]

        result = self._runner.run_powershell_command(command, check=False)
        raw_output = result.stdout.strip() if result else "No Result"

        if result and result.returncode == 0 and raw_output:
            try:
                return json.loads(raw_output)
            except json.JSONDecodeError:
                logger.exception(
                    "Failed to decode JSON output for task '%s'. Raw Output: %s",
                    task_name,
                    raw_output,
                )
                return None

        if result and "No MSFT_ScheduledTask objects found" in result.stderr:
            logger.warning("Scheduled Task '%s' not found", task_name)
            return None

        logger.warning(
            "Could not fetch task data for '%s'. Task may not exist or PowerShell failed. Raw STDOUT: %s",
            task_name,
            raw_output,
        )
        return None

    def get_task_status(self, task_data: dict | None) -> str:
        if not task_data:
            return "NOT FOUND"
        return TASK_STATE_MAP.get(task_data.get("State"), "UNKNOWN")

    def get_last_run_time(self, task_data: dict | None, task_name: str) -> str | None:
        if not task_data:
            return None

        last_run_time = task_data.get("LastRunTime")
        if not last_run_time or last_run_time.startswith("0001"):
            return None

        try:
            dt_obj_aware = datetime.fromisoformat(last_run_time)
            return dt_obj_aware.astimezone().isoformat(timespec="microseconds")
        except ValueError as exc:
            logger.warning(
                "Could not parse LastRunTime '%s' for task '%s'. Error: %s",
                last_run_time,
                task_name,
                exc,
            )
            return last_run_time

    def get_last_run_result(self, task_data: dict | None) -> str | None:
        if not task_data:
            return None
        last_run_result = task_data.get("LastTaskResult")
        return str(last_run_result) if last_run_result is not None else None

    def run_action(self, task_name: str, command: list[str]) -> bool:
        result = self._runner.run_powershell_command(command)
        return result is not None and result.returncode == 0
