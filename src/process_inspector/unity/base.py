# import json
import logging
from pathlib import Path

from process_inspector.appcontrol import NativeApp

logger = logging.getLogger(__name__)


class UnityAppBase(NativeApp):
    """Basic control of a Unity App"""

    def __init__(self, app_path: Path, developer: str = "X Studios"):
        super().__init__(app_path)
        # Unity apps have a streaming assets path
        self.config_path = self.get_config_path()
        self.developer = developer

    def get_developer_variations(self) -> list[str]:
        """No one gets the developer name right, so crteate some variations."""
        # Examples: "X Studios", "XStudios", "X-Studios", "X_Studios"
        developer_variations = [
            self.developer,
            self.developer.replace(" ", ""),
            self.developer.replace(" ", "-"),
            self.developer.replace(" ", "_"),
        ]
        lower_case_variations = [d.lower() for d in developer_variations]
        return developer_variations + lower_case_variations

    def get_streaming_assets_path(self) -> Path:
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    def get_config_path(self) -> Path:
        """Return path to config.json that we always implement."""
        return self.get_streaming_assets_path() / "config.json"

    def get_player_log_path(self) -> Path:
        """Get path to player log file."""
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    def get_player_prev_log_path(self) -> Path:
        """Get path to player log file."""
        msg = "This method should return a Path"
        raise NotImplementedError(msg)

    # def get_file_content(self, filename: str) -> str:
    #     """Get file content from streaming assets path."""
    #     filepath = self.get_streaming_assets_path() / filename
    #     if filepath.is_file():
    #         with filepath.open(encoding="utf8") as fh:
    #             return fh.read().strip()
    #     return ""

    # def get_config(self) -> dict:
    #     """Get config contents."""
    #     config_content = self.get_file_content("config.json")
    #     return json.loads(config_content) if config_content else {}

    def get_version(self) -> str:
        """Get app version from file. Must be a better way?"""
        return self.get_file_content("version.txt") or "--"
