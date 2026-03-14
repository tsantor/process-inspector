from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppIdentity:
    """Immutable app identity derived from the application path."""

    app_path: Path
    app_exe: str
    app_name: str

    @classmethod
    def from_path(cls, app_path: Path) -> AppIdentity:
        return cls(app_path=app_path, app_exe=app_path.name, app_name=app_path.stem)
