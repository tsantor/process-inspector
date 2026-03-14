from __future__ import annotations

import logging

from process_inspector.taskcontrol.application.dtos import TaskInfoDTO
from process_inspector.taskcontrol.interface.dependencies import get_task_service

logger = logging.getLogger(__name__)


class ScheduledTask:
    def __init__(self, name: str, state_change_callback=None):
        self.name = name
        self._on_state_change_cb = state_change_callback
        self._last_running_state: bool | None = None
        self._task_data: dict | None = None
        self._service = get_task_service()
        self._fetch_task_data()

    def _fetch_task_data(self) -> None:
        self._task_data = self._service.fetch_task_data(self.name)

    def _get_task_status(self) -> str:
        return self._service.get_task_status(self._task_data)

    def status(self):
        return self._get_task_status()

    def _get_last_run_time(self) -> str | None:
        return self._service.get_last_run_time(self._task_data, self.name)

    def _get_last_run_result(self) -> str | None:
        return self._service.get_last_run_result(self._task_data)

    def _check_state_change(self) -> bool:
        if not self._task_data:
            return False

        current_running = self._get_task_status() == "RUNNING"
        if self._last_running_state != current_running:
            logger.debug(
                "Scheduled Task '%s' running state changed to: %s",
                self.name,
                current_running,
            )
            if self._on_state_change_cb:
                self._on_state_change_cb(task=self, is_running=current_running)
            self._last_running_state = current_running
            return True
        return False

    def refresh(self) -> None:
        self._fetch_task_data()

    def is_running(self) -> bool:
        return self._get_task_status() == "RUNNING"

    def start(self) -> bool:
        logger.info("Starting Task Scheduler Task: %s", self.name)
        success = self._service.run_action(
            self.name,
            [f"Start-ScheduledTask -TaskName '{self.name}'"],
        )
        self._fetch_task_data()
        self._check_state_change()
        return success

    def stop(self) -> bool:
        logger.info("Stopping Task Scheduler Task: %s", self.name)
        success = self._service.run_action(
            self.name,
            [f"Stop-ScheduledTask -TaskName '{self.name}'"],
        )
        self._fetch_task_data()
        self._check_state_change()
        return success

    def restart(self) -> bool:
        logger.info("Restarting Task Scheduler Task: %s", self.name)
        if self.stop():
            return self.start()
        return False

    def __repr__(self):
        return f"ScheduledTask('{self.name}')"

    def as_dict(self) -> dict:
        return TaskInfoDTO(
            name=self.name,
            status=self._get_task_status(),
            is_running=self.is_running(),
            last_run_time=self._get_last_run_time(),
            last_run_result=self._get_last_run_result(),
        ).as_dict()
