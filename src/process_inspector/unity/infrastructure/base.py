# import json
import logging
from pathlib import Path

from process_inspector.appcontrol import NativeApp
from process_inspector.unity.infrastructure.factory import build_unity_path_service
from process_inspector.unity.infrastructure.repository import read_text_file

logger = logging.getLogger(__name__)


class UnityAppBase(NativeApp):
    """Basic control of a Unity App"""

    def __init__(self, app_path: Path, developer: str = "X Studios"):
        super().__init__(app_path)
        self._path_service = build_unity_path_service()
        # Unity apps have a streaming assets path
        self.config_path = self.get_config_path()
        self.developer = developer

    def get_developer_variations(self) -> list[str]:
        """No one gets the developer name right, so crteate some variations."""
        return self._path_service.get_developer_variations(self.developer)

    def get_streaming_assets_path(self) -> Path:
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    def get_config_path(self) -> Path:
        """Return path to config.json that we always implement."""
        return self._path_service.build_config_path(self.get_streaming_assets_path())

    def get_file_content(self, filename: str) -> str:
        filepath = self.get_streaming_assets_path() / filename
        return read_text_file(filepath)

    def get_player_log_path(self) -> Path:
        """Get path to player log file."""
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    def get_player_prev_log_path(self) -> Path:
        """Get path to player log file."""
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    def get_version(self) -> str:
        """Get app version from file. Must be a better way?"""
        return self.get_file_content("version.txt") or "--"
