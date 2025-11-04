import logging
from pathlib import Path

from .base import UnityAppBase

logger = logging.getLogger(__name__)


class UnityApp(UnityAppBase):
    """Basic control of a Windows Unity App"""

    def get_streaming_assets_path(self) -> Path:
        return self.app_path.parent / f"{self.app_path.stem}_Data" / "StreamingAssets"

    def _get_appdata_path(self) -> Path:
        return next(
            (
                Path(f"~/AppData/LocalLow/{dev}/{self.app_path.stem}").expanduser()
                for dev in self.get_developer_variations()
                if (
                    Path(f"~/AppData/LocalLow/{dev}/{self.app_path.stem}")
                    .expanduser()
                    .is_dir()
                )
            ),
            Path(
                f"~/AppData/LocalLow/{self.developer}/{self.app_path.stem}"
            ).expanduser(),
        )

    def get_player_log_path(self) -> Path:
        """Get path to player log file."""
        return self._get_appdata_path() / "Player.log"

    def get_player_prev_log_path(self) -> Path:
        """Get path to player log file."""
        return self._get_appdata_path() / "Player-prev.log"
