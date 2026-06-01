from __future__ import annotations

from process_inspector.teamviewer.runtime.factory import build_teamviewer_controller


class Teamviewer:
    """Basic control of TeamViewer across platforms."""

    def __init__(self, state_change_callback=None):
        self._controller = build_teamviewer_controller(
            state_change_callback=state_change_callback
        )

    @property
    def app(self):
        return self._controller

    def get_pid(self) -> int | None:
        pid = getattr(self._controller, "pid", None)
        return pid() if callable(pid) else pid

    def is_running(self) -> bool:
        return self._controller.is_running()

    def open(self) -> bool:
        return self._controller.open()

    def close(self) -> bool:
        return self._controller.close()


__all__ = ["Teamviewer"]
