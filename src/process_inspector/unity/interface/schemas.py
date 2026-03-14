from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnityPathsSchema:
    streaming_assets_path: str
    config_path: str
