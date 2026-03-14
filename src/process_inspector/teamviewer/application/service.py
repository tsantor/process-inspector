from __future__ import annotations

from process_inspector.teamviewer.domain.entities import TeamviewerRuntime


class TeamviewerService:
    def __init__(self, controller):
        self._runtime = TeamviewerRuntime(instance=controller)

    @property
    def app(self):
        return self._runtime.instance

    def get_pid(self) -> int | None:
        instance = self._runtime.instance
        pid = getattr(instance, "pid", None)
        return pid() if callable(pid) else pid

    def is_running(self) -> bool:
        return self._runtime.instance.is_running()

    def open(self) -> bool:
        return self._runtime.instance.open()

    def close(self) -> bool:
        return self._runtime.instance.close()
