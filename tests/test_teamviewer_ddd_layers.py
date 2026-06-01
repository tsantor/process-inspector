from __future__ import annotations

from unittest.mock import patch

from process_inspector.teamviewer.teamviewer import Teamviewer


class DummyController:
    pid = 555

    def is_running(self) -> bool:
        return True

    def open(self) -> bool:
        return True

    def close(self) -> bool:
        return True


def test_teamviewer_delegates_to_controller():
    expected_pid = 555
    with patch(
        "process_inspector.teamviewer.teamviewer.build_teamviewer_controller",
        return_value=DummyController(),
    ):
        teamviewer = Teamviewer()

        assert teamviewer.get_pid() == expected_pid
        assert teamviewer.is_running() is True
        assert teamviewer.open() is True
        assert teamviewer.close() is True
