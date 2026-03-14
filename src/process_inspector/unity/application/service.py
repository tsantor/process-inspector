from __future__ import annotations

from typing import TYPE_CHECKING

from process_inspector.unity.domain.entities import UnityPaths

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

    def build_paths(self, streaming_assets_path: Path) -> UnityPaths:
        return UnityPaths(
            streaming_assets_path=streaming_assets_path,
            config_path=streaming_assets_path / "config.json",
        )
