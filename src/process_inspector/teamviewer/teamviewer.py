import sys

from process_inspector.appcontrol import NativeApp
from process_inspector.servicecontrol.implementations import SystemCtl
from process_inspector.teamviewer import get_teamviewer_path


class Teamviewer:
    """Basic control of TeamViewer across platforms"""

    def __init__(self):
        if sys.platform == "linux":
            self._instance = SystemCtl("teamviewerd.service")
        else:
            self._instance = NativeApp(get_teamviewer_path())

    def get_pid(self) -> int | None:
        return self._instance.get_pid()

    def is_running(self) -> bool:
        return self._instance.is_running()

    def open(self) -> bool:
        return self._instance.open()

    def close(self) -> bool:
        return self._instance.close()
