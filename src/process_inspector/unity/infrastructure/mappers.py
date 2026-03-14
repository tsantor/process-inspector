from __future__ import annotations

from process_inspector.unity.domain.entities import UnityPaths


def to_unity_paths(streaming_assets_path, config_path) -> UnityPaths:
    return UnityPaths(
        streaming_assets_path=streaming_assets_path,
        config_path=config_path,
    )
