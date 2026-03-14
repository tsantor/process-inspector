from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeamviewerInfo:
    id: str
    version: str
    path: str
    is_installed: bool
