from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TeamviewerSchema:
    id: str
    version: str
    path: str
    is_installed: bool
