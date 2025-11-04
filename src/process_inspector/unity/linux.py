import logging
from pathlib import Path

from .base import UnityAppBase

logger = logging.getLogger(__name__)


class UnityApp(UnityAppBase):
    """Basic control of a Linux Unity App"""

    def get_streaming_assets_path(self) -> Path:
        return self.app_path.parent / f"{self.app_path.stem}_Data" / "StreamingAssets"
