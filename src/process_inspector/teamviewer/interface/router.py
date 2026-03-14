from __future__ import annotations

from process_inspector.teamviewer.interface.dependencies import get_teamviewer_service


class Teamviewer:
    """Basic control of TeamViewer across platforms."""

    def __init__(self, state_change_callback=None):
        self._service = get_teamviewer_service(
            state_change_callback=state_change_callback,
        )

    @property
    def app(self):
        return self._service.app

    def get_pid(self) -> int | None:
        return self._service.get_pid()

    def is_running(self) -> bool:
        return self._service.is_running()

    def open(self) -> bool:
        return self._service.open()

    def close(self) -> bool:
        return self._service.close()
