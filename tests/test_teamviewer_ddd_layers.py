from __future__ import annotations

from process_inspector.teamviewer.application.service import TeamviewerService
from process_inspector.teamviewer.infrastructure.mappers import to_teamviewer_info


class DummyController:
    pid = 555

    def is_running(self) -> bool:
        return True

    def open(self) -> bool:
        return True

    def close(self) -> bool:
        return True


def test_teamviewer_service_delegates_to_controller():
    expected_pid = 555
    service = TeamviewerService(controller=DummyController())

    assert service.get_pid() == expected_pid
    assert service.is_running() is True
    assert service.open() is True
    assert service.close() is True


def test_teamviewer_info_mapper_defaults():
    info = to_teamviewer_info({"id": "123", "version": "1.2.3", "is_installed": 1})
    assert info.id == "123"
    assert info.version == "1.2.3"
    assert info.path == ""
    assert info.is_installed is True
