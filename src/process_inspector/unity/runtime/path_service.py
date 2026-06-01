from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class UnityPathService:
    def get_developer_variations(self, developer: str) -> list[str]:
        variations = [
            developer,
            developer.replace(" ", ""),
            developer.replace(" ", "-"),
            developer.replace(" ", "_"),
        ]
        return variations + [item.lower() for item in variations]

    def build_config_path(self, streaming_assets_path: Path) -> Path:
        return streaming_assets_path / "config.json"
