import logging
import sys

from process_inspector.appcontrol import NativeApp
from process_inspector.servicecontrol.implementations import SystemCtl
from process_inspector.teamviewer import get_teamviewer_path

logger = logging.getLogger(__name__)


class Teamviewer:
    """Basic control of TeamViewer across platforms"""

    def __init__(self, state_change_callback=None):
        if sys.platform == "linux":
            self._instance = SystemCtl(
                "teamviewerd.service",
                state_change_callback=state_change_callback,
            )
        else:
            self._instance = NativeApp(
                get_teamviewer_path(),
                state_change_callback=state_change_callback,
                # state_change_callback=self._on_running_state_changed,
            )

    @property
    def app(self) -> NativeApp:
        return self._instance

    def get_pid(self) -> int | None:
        return self._instance.get_pid()

    def is_running(self) -> bool:
        return self._instance.is_running()

    def open(self) -> bool:
        return self._instance.open()

    def close(self) -> bool:
        return self._instance.close()

    # def _on_running_state_changed(self, app, is_running: bool) -> None:
    #     """Called when the running state changes."""
    #     logger.info("Teamviewer: App %s running: %s", app, is_running)
