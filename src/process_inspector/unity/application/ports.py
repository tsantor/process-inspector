from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from pathlib import Path


class UnityPathPort(Protocol):
    def build_config_path(self, streaming_assets_path: Path) -> Path: ...
