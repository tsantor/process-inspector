from __future__ import annotations

from process_inspector.oscontrol.application.service import RebootService
from process_inspector.oscontrol.domain.entities import RebootResult
from process_inspector.oscontrol.domain.value_objects import RebootRequest


class DummyRunner:
    def __init__(self, result: bool):
        self.result = result
        self.last_request = None

    def run_command(self, request: RebootRequest) -> bool:
        self.last_request = request
        return self.result


def test_reboot_request_value_object():
    request = RebootRequest(command=("sudo", "reboot"))
    assert request.command == ("sudo", "reboot")


def test_reboot_result_entity():
    result = RebootResult(succeeded=True)
    assert result.succeeded is True


def test_reboot_service_success():
    runner = DummyRunner(result=True)
    service = RebootService(command_runner=runner)

    assert service.reboot(["sudo", "reboot"]) is True
    assert runner.last_request == RebootRequest(command=("sudo", "reboot"))


def test_reboot_service_failure():
    runner = DummyRunner(result=False)
    service = RebootService(command_runner=runner)

    assert service.reboot(["sudo", "reboot"]) is False
