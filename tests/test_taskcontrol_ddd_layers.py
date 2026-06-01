from __future__ import annotations

from process_inspector.taskcontrol.infrastructure.task_service import (
    ScheduledTaskService,
)


class DummyRunner:
    def __init__(self, result):
        self.result = result

    def run_powershell_command(self, command, check=True):
        return self.result


class DummyResult:
    def __init__(self, stdout: str, returncode: int = 0, stderr: str = ""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_get_task_status_from_service_data():
    service = ScheduledTaskService(powershell_runner=DummyRunner(None))
    assert service.get_task_status({"State": 4}) == "RUNNING"


def test_fetch_task_data_parses_json():
    expected_state = 3
    result = DummyResult(stdout='{"State": 3, "LastTaskResult": 0}')
    service = ScheduledTaskService(powershell_runner=DummyRunner(result))

    data = service.fetch_task_data("Example")

    assert data is not None
    assert data["State"] == expected_state
    assert data["LastTaskResult"] == 0


def test_run_action_success_when_return_code_zero():
    result = DummyResult(stdout="", returncode=0)
    service = ScheduledTaskService(powershell_runner=DummyRunner(result))
    assert service.run_action("Example", ["Start-ScheduledTask"]) is True
